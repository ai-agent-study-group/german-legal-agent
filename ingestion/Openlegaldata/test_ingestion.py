"""Offline regression tests. No API requests or changes to checked-in datasets."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import fetch_cases as cases
import normalize
import summarize


def document(number, summary=False):
    row = {
        "id": f"oldp:case:{number}", "type": "case", "title": "BGH",
        "text": "Die Entscheidung betrifft § 536 BGB.", "court": "Bundesgerichtshof",
        "date": "2020-01-01", "decision_type": "Urteil", "source": normalize.SOURCE,
        "source_url": "https://example.org/", "cited_laws": ["BGB § 536"],
        "topics": ["Mietminderung"], "file_number": "same number", "ecli": "legacy",
    }
    if summary:
        row.update(text_type="ai_summary", language="de")
    return row


class IncrementalTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        for name, value in (
            ("RAW_OUTPUT_FILE", root / "samples" / "raw.json"),
            ("CASE_ARCHIVE", root / "archive.json"),
        ):
            patcher = patch.object(cases, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.env = patch.dict(os.environ, OPENAI_API_KEY="test-key", OLDP_SUMMARY_MODEL="test-model")
        self.env.start()
        self.addCleanup(self.env.stop)

    def read(self, filename):
        return json.loads((cases.RAW_OUTPUT_FILE.parent / filename).read_text(encoding="utf-8"))

    def test_atomic_save_retries_transient_windows_lock(self):
        target = cases.RAW_OUTPUT_FILE.parent / cases.CASES_FILE
        cases.save_json([document(1, True)], target)
        original = target.read_bytes()
        replace = Path.replace
        attempts = []

        def locked_then_available(source, destination):
            attempts.append(source)
            # A reader must continue seeing the previous complete JSON.
            self.assertEqual(target.read_bytes(), original)
            if len(attempts) < 3:
                raise PermissionError(13, "Access denied")
            return replace(source, destination)

        with patch.object(Path, "replace", locked_then_available), patch.object(cases.time, "sleep") as sleep:
            cases.save_json([document(1, True), document(2, True)], target)
        self.assertEqual(len(attempts), 3)
        self.assertEqual(len(set(attempts)), 1)
        self.assertEqual(sleep.call_count, 2)
        self.assertEqual(len(self.read(cases.CASES_FILE)), 2)
        self.assertFalse(list(target.parent.glob("*.tmp")))

    def test_atomic_save_preserves_old_and_pending_json_when_locked(self):
        target = cases.RAW_OUTPUT_FILE.parent / cases.CASES_FILE
        cases.save_json([document(1, True)], target)
        original = target.read_bytes()
        with patch.object(Path, "replace", side_effect=PermissionError(13, "Access denied")), patch.object(cases.time, "sleep") as sleep:
            with self.assertRaisesRegex(normalize.IngestionError, "Pending JSON preserved"):
                cases.save_json([document(2, True)], target)
        self.assertEqual(target.read_bytes(), original)
        pending = list(target.parent.glob("*.tmp"))
        self.assertEqual(len(pending), 1)
        self.assertEqual(json.loads(pending[0].read_text(encoding="utf-8"))[0]["id"], "oldp:case:2")
        self.assertEqual(sleep.call_count, len(cases.SAVE_RETRY_DELAYS))

    @staticmethod
    def detail(kind, row):
        return {
            "id": row["id"], "court": {"name": "Bundesgerichtshof"},
            "date": "2020-01-01", "content": "<p>§ 536 BGB</p>", "type": "Urteil",
        }

    def test_duplicate_pages_and_incremental_rerun(self):
        cases.save_json([document(1, True)], cases.RAW_OUTPUT_FILE.parent / cases.CASES_FILE)
        requests = []

        def api(path, params=None):
            requests.append(path)
            ids = [1] if params else [2, 3]
            return {
                "results": [{"id": n, "court": "BGH", "text": "§ 536 BGB"} for n in ids],
                "next": "cases/search/?offset=1" if params else None,
            }

        with patch.object(normalize, "get_json", api), patch.object(cases, "detail", side_effect=self.detail) as detail, patch.object(cases, "summarize_case", return_value="Neue Zusammenfassung") as ai:
            self.assertEqual(cases.collect_mietrecht(laws=False, case_limit=1, topics=["Mietminderung"]), 0)
            self.assertEqual(len(requests), 2)
            self.assertEqual(detail.call_count, 1)
            self.assertEqual(ai.call_count, 1)
            self.assertEqual([row["id"] for row in self.read(cases.CASES_FILE)], ["oldp:case:1", "oldp:case:2"])
            self.assertEqual(cases.collect_mietrecht(laws=False, case_limit=1, topics=["Mietminderung"]), 0)
            self.assertEqual(ai.call_count, 2)
            rows = self.read(cases.CASES_FILE)
            self.assertEqual(len(rows), 3)
            self.assertTrue(all("ecli" not in row and "file_number" not in row for row in rows))
            stats = self.read("ingestion_summary.json")
            self.assertEqual(stats["new_cases_added"], 1)
            self.assertEqual(stats["duplicate_cases_skipped"], 2)

    def test_migration_and_failed_summary_raw_retry(self):
        cases.save_json([document(1), document(2, True)], cases.RAW_OUTPUT_FILE.parent / cases.CASES_FILE)
        with patch.object(cases, "search_candidates", return_value=iter(())), patch.object(cases, "summarize_case", side_effect=normalize.IngestionError("invalid summary")) as ai:
            self.assertEqual(cases.collect_mietrecht(laws=False), 1)
            self.assertEqual(ai.call_count, 1)
            self.assertEqual([row["id"] for row in self.read(cases.CASES_FILE)], ["oldp:case:2"])
            self.assertEqual(json.loads(cases.CASE_ARCHIVE.read_text(encoding="utf-8"))[0]["text"], document(1)["text"])
            self.assertEqual(self.read("parsing_failures.json")[0]["record_type"], "case_summary")
        with patch.object(cases, "search_candidates", return_value=iter(())), patch.object(cases, "summarize_case", return_value="Zusammenfassung") as ai:
            self.assertEqual(cases.collect_mietrecht(laws=False), 0)
            self.assertEqual(ai.call_count, 1)
            self.assertEqual(len(self.read(cases.CASES_FILE)), 2)
            self.assertEqual(self.read("ingestion_summary.json")["new_cases_added"], 0)

    def test_more_than_fifty_new_cases_and_search_exhaustion(self):
        offsets = []

        def api(path, params=None):
            offset = 0 if params else int(path.rsplit("=", 1)[1])
            offsets.append(offset)
            return {
                "results": [
                    {"id": n, "court": "BGH", "text": "§ 536 BGB"}
                    for n in range(offset + 1, offset + 26)
                ],
                "next": f"cases/search/?offset={offset + 25}" if offset < 50 else None,
            }

        with patch.object(normalize, "get_json", api), patch.object(cases, "detail", side_effect=self.detail), patch.object(cases, "summarize_case", return_value="Zusammenfassung") as ai:
            self.assertEqual(cases.collect_mietrecht(laws=False, case_limit=60, topics=["Mietminderung"]), 0)
            self.assertEqual(len(self.read(cases.CASES_FILE)), 60)
            self.assertEqual(offsets, [0, 25, 50])
            self.assertEqual(ai.call_count, 60)
            # The next run exhausts both topic streams and adds only remaining IDs.
            self.assertEqual(cases.collect_mietrecht(laws=False, case_limit=60, topics=["Mietminderung"]), 0)
            self.assertEqual(len(self.read(cases.CASES_FILE)), 75)
            self.assertEqual(ai.call_count, 75)

    def test_ai_service_failure_stops_calls(self):
        cases.save_json([document(1), document(2)], cases.RAW_OUTPUT_FILE.parent / cases.CASES_FILE)
        with patch.object(cases, "summarize_case", side_effect=summarize.SummaryServiceError("AI summary HTTP 429")) as ai, patch.object(cases, "search_candidates") as search:
            self.assertEqual(cases.collect_mietrecht(laws=False), 1)
            self.assertEqual(ai.call_count, 1)
            search.assert_not_called()
            self.assertEqual(len(json.loads(cases.CASE_ARCHIVE.read_text(encoding="utf-8"))), 2)

    def test_search_error_preserves_completed_cases(self):
        cases.save_json([document(1, True)], cases.RAW_OUTPUT_FILE.parent / cases.CASES_FILE)
        with patch.object(normalize, "get_json", side_effect=normalize.RateLimitError(normalize.RATE_LIMIT_MESSAGE)):
            self.assertEqual(cases.collect_mietrecht(laws=False), 1)
            self.assertEqual(len(self.read(cases.CASES_FILE)), 1)
            self.assertEqual(self.read("ingestion_summary.json")["total_cases"], 1)

    def test_case_run_does_not_touch_laws(self):
        path = cases.RAW_OUTPUT_FILE.parent / cases.LAW_FILES["primary"]
        cases.save_json([{"id": "law:1", "text": "Original law"}], path)
        before = path.read_bytes()
        with patch.object(cases, "search_candidates", return_value=iter(())), patch.object(cases, "collect_laws") as laws:
            self.assertEqual(cases.collect_mietrecht(laws=False), 0)
            laws.assert_not_called()
        self.assertEqual(path.read_bytes(), before)

    def test_missing_key_never_calls_api_or_rewrites_cases(self):
        path = cases.RAW_OUTPUT_FILE.parent / cases.CASES_FILE
        cases.save_json([document(1)], path)
        before = path.read_bytes()
        with patch.dict(os.environ, OPENAI_API_KEY=""), patch.object(cases, "search_candidates") as search:
            self.assertEqual(cases.collect_mietrecht(laws=False), 1)
            search.assert_not_called()
            self.assertEqual(path.read_bytes(), before)

    def test_process_lock(self):
        with cases.ingestion_file_lock():
            self.assertEqual(cases.collect_mietrecht(laws=False), 1)

    def test_summary_response_validation(self):
        from io import BytesIO
        for status, words, valid in (("completed", 350, True), ("incomplete", 350, False), ("completed", 10, False)):
            payload = {"status": status, "output": [{"type": "message", "content": [
                {"type": "output_text", "text": " ".join(["Sachverhalt"] * words)}
            ]}]}
            with self.subTest(status=status, words=words), patch.object(summarize, "urlopen", return_value=BytesIO(json.dumps(payload).encode())):
                if valid:
                    self.assertEqual(len(summarize.summarize_case(document(1)).split()), words)
                else:
                    with self.assertRaises(normalize.IngestionError):
                        summarize.summarize_case(document(1))


if __name__ == "__main__":
    unittest.main()
