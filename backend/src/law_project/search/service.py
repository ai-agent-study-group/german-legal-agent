"""
키워드 검색. JSON 데이터셋용 단순 구현.

tokenize() - 검색어를 소문자 단어로, stopword 제거
words() - 문서의 단어를 소문자 set으로
count_matches() - 단어리스트에서 검색어로 시작하는 단어가 몇개
score() - 문서 하나의 점수. 검색어마다 점수를 더함.
make_excerpt() - 검색어 주변 1000자만 잘라서 돌려줌
rank() - 문서목록을 검색어로 점수 매기고, 조문/판례별로 상위 3개씩 뽑아서 SearchHit 목록으로 돌려줌
get_document() - JSON 파일을 읽어서 Document 목록으로 돌려줌
search() - agent가 부르는 함수. 조문 최대 3개 + 판례 최대 3개를 SearchHit 목록으로 돌려줌
read() - agent가 부르는 함수. id로 문서 전문을 돌려줌. 없으면 None. 

"""

import re
from functools import lru_cache

from law_project.core.config import get_settings
from law_project.schemas.document import Document
from law_project.schemas.search import SearchHit
from law_project.search.loader import load_documents

EXCERPT_LENGTH = 1000  # 검색 결과에 넣을 본문 길이 (전문은 read(id)로)
TITLE_WEIGHT = 3  # 제목에 나오면 +3점
MAX_COUNT = 5  # 본문에서 같은 단어는 5번까지만 셈. (긴 판례가 무조건 이기지 않게)
MATCH_BONUS = 5  # 검색어 하나 걸릴때마다 +5
STOPWORDS = {"der", "die", "das", "und", "oder", "den", "dem", "des", "ein", "eine", "einen", "ist", "mit", "von", "für", "auf", "bei", "nicht"}

def tokenize(text:str) -> list[str] :
   words = re.findall(r"\w+", text.lower())
   return[w for w in words if len(w)>=3 and w not in STOPWORDS]
    # 1-2글자는 무시.

def words (text:str) -> list[str]:
    return re.findall(r"\w+", text.lower())

# 그 단어로 시작하는게 몇개인가?
def count_matches(term:str, word_list:list[str]) -> int:
    return sum(1 for w in word_list if w.startswith(term))
# startswith를 쓰면, "kündigung"이 "ankündigung"에는 안 걸리지만 "kündigungsfrist"(해지 기한)에는 걸림.

def score(document: Document, terms: list[str]) -> int:
    title_words = words(document.title)
    text_words = words(document.text)
    total = 0
    for t in terms:
        in_title = count_matches(t, title_words) > 0
        count = min(count_matches(t, text_words), MAX_COUNT)
        # 본문에 100번나와도 Maxcount로 자름 - 긴 판례가 단어수가 많아서 무조건 이기는것을 막음.
        if in_title or count:
            total += MATCH_BONUS + TITLE_WEIGHT * in_title + count
    return total
# 문서 하나의 점수. - 검색어마다 점수를 더함.

def make_excerpt(text: str, terms: list[str]) -> str:
    lower = text.lower()
    positions = [m.start() for t in terms if (m := re.search(r"\b" + re.escape(t), lower))]
    # 검색어들이 본문에서 처음나온위치 찾음. \b는 단어시작 , m은 찾은 결과를 m에 넣으면서 동시에 있는지 확인.
    start = max(min(positions) - 100, 0) if positions else 0
    # 가장 먼저 나온 위치에서 100글자 앞부터 (앞뒤문맥도 조금 보이게하기위해서.)
    excerpt = text[start : start + EXCERPT_LENGTH]
    if start > 0:
        excerpt = "..." + excerpt
    if start + EXCERPT_LENGTH < len(text):
        excerpt += "..."
    return excerpt

# 고르고 정렬.
def rank(documents: list[Document], query: str, domain: str, per_type: int = 3) -> list[SearchHit]:
    terms = tokenize(query)
    if not terms:
        return []
    # 검색어정리.

    # 조문먼저, 그다음 판례 
    hits: list[SearchHit] = []
    for doc_type in ("law", "case"):
        scored = []
        for doc in documents:
            if doc.domain != domain or doc.type != doc_type:
                continue
            s = score(doc, terms)
            if s > 0:
                scored.append((s, doc))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        # key=lambda pair: pair[0]: "짝의 첫 번째(점수)로 정렬해"
        # reverse=True: 큰 게 앞으로

        for s, doc in scored[:per_type]:
            hits.append(
                SearchHit(
                    id=doc.id,
                    type=doc.type,
                    title=doc.title,
                    excerpt=make_excerpt(doc.text, terms),
                    score=s,
                    source_url=doc.source_url,
                )
            )
    return hits

# scored[:per_type]: 앞에서 5개만
# 각각 SearchHit 쪽지로 만들어서 hits에 담기. 여기서 schemas/search.py의 양식이 쓰임.
# 본문은 make_excerpt로 1000자만
# 끝나면 조문3/판례3 총 6개.

@lru_cache
def get_documents () -> list[Document]:
  return load_documents(get_settings().data_dir)

def search (query: str, domain:str, per_type =3) -> list[SearchHit]:
    #agent가 부를 함수. 조문 최대 per_type개 +  판례 최대 per_type개
    return rank(get_documents(), query, domain, per_type)

def read (doc_id: str) -> Document | None:
   # agent가 부를 함수, id로 문서 전문을 돌려줌. 없으면 None.
    for doc in get_documents():
       if doc.id == doc_id:
           return doc   
    return None