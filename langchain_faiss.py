import sqlite3
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI
from langchain.schema import Document
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()

def fetch_translations_from_db():
    """SQLite 데이터베이스에서 번역 데이터를 가져옵니다."""
    conn = sqlite3.connect('text_chunks.db')  # SQLite 데이터베이스 연결
    cursor = conn.cursor()
    cursor.execute("SELECT original_text, translation FROM chunks WHERE translation IS NOT NULL")  # 번역이 있는 데이터만 선택
    data = cursor.fetchall()  # 데이터 가져오기
    conn.close()  # 데이터베이스 연결 닫기
    return data

# 데이터베이스에서 번역 데이터 로드
translations = fetch_translations_from_db()
documents = [Document(
    page_content=f"{orig}\n{trans}",  # 원문과 번역문을 결합
    metadata={"translated": True}  # 메타데이터에 번역 여부 표시
) for orig, trans in translations]

# 텍스트를 작은 조각으로 분할
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)  # 조각 크기와 중첩 설정
chunks = text_splitter.split_documents(documents)  # 문서를 조각으로 분할

# 임베딩 생성
embeddings = OpenAIEmbeddings(
    openai_api_key=os.getenv("OPENAI_API_KEY")  # OpenAI API 키 사용
)
vector_db = FAISS.from_documents(chunks, embeddings)  # FAISS 벡터 데이터베이스 생성

# 유사도 검색 체인 생성
retriever = vector_db.as_retriever()  # 검색기 생성
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY")),  # OpenAI LLM 사용
    retriever=retriever  # 검색기 연결
)

# 예제 쿼리 실행
query = "토큰화란 무엇인가?"  # 쿼리 입력
response = qa_chain.run(query)  # 쿼리 실행 및 응답 받기
print(response)  # 응답 출력
