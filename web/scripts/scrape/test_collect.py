import json
import tempfile
import unittest
from pathlib import Path
from collect import collect, extract_body
from review import approve

SPEC={"id":"housing-test","domain":"housing","url":"https://www.gesetze-im-internet.de/bgb/__551.html","title":"test","keywords":["보증금"],"language":"de","selector":"main"}
HTML="<html><nav>menu</nav><main><p>" + "Official body with sufficient information. " * 3 + "</p><script>bad</script></main></html>"

class CollectorTests(unittest.TestCase):
    def test_legacy_encoding(self):
        html=('<meta charset="iso-8859-1"><main>' + "Begrenzung für Mietsicherheiten. " * 3 + "</main>").encode("iso-8859-1")
        self.assertIn("für", extract_body(html, "main"))

    def test_challenge_page_is_not_saved(self):
        with self.assertRaisesRegex(ValueError, "차단"):
            extract_body("<title>Radware Page</title><main>Verifying your browser</main>", "main")

    def test_missing_selector_is_failure(self):
        with self.assertRaises(ValueError):
            extract_body(HTML, ".missing")

    def test_failed_collection_preserves_existing(self):
        with tempfile.TemporaryDirectory() as d:
            pending=Path(d)/"pending";pending.mkdir()
            path=pending/"housing-test.json";path.write_text('{"old":true}')
            failures=collect([SPEC],pending,lambda url: (_ for _ in ()).throw(OSError("offline")))
            self.assertEqual(failures,1)
            self.assertEqual(json.loads(path.read_text()),{"old":True})

    def test_collect_then_explicit_review(self):
        with tempfile.TemporaryDirectory() as d:
            data=Path(d); pending=data/"pending"
            app=data/"housing.json"; app.write_text("[]")
            self.assertEqual(collect([SPEC],pending,lambda url: HTML),0)
            candidate=json.loads((pending/"housing-test.json").read_text())
            self.assertFalse(candidate["reviewed"])
            self.assertEqual(json.loads(app.read_text()),[])
            self.assertNotIn("bad",candidate["body"])
            approve("housing-test",data)
            reviewed=json.loads(app.read_text())
            self.assertTrue(reviewed[0]["reviewed"])
            self.assertTrue(reviewed[0]["reviewedAt"])

    def test_path_traversal_blocked(self):
        with self.assertRaises(ValueError):
            approve("../outside")

if __name__ == "__main__":
    unittest.main()
