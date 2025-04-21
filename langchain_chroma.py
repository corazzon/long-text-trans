import logging
from chromadb.utils import embedding_functions
from chromadb import Chroma

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 임베딩 함수 설정
embeddings = embedding_functions.DefaultEmbeddingFunction()

# --- Database Initialization ---
DB_DIR = "chroma_db"
COLLECTION_NAME = "translations"

try:
    # 기존 데이터베이스 로드
    vector_db = Chroma(
        persist_directory=DB_DIR,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )
    
    # 데이터베이스 존재 여부 확인
    collection_count = len(vector_db.get()['ids'])
    logging.info(f"Successfully loaded existing Chroma database with {collection_count} documents.")
    
except Exception as e:
    logging.error(f"Failed to load Chroma database from {DB_DIR}: {e}")
    vector_db = None
