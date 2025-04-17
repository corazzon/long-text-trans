import os
import sqlite3
from openai import OpenAI
import tiktoken

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수에서 OPENAI_API_KEY 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI API 키 설정
client = OpenAI(api_key=OPENAI_API_KEY)
client

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def get_first_txt_file(directory='.'):
    txt_files = [f for f in os.listdir(directory) if f.endswith('_subtitle.txt')]
    txt_files.sort()  # 파일명 알파벳 순으로 정렬
    return txt_files[0] if txt_files else None

def create_chunks(text, chunk_size=1000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def create_db_and_table():
    conn = sqlite3.connect('text_chunks.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS chunks
                      (id INTEGER PRIMARY KEY,
                       original_text TEXT,
                       length INTEGER,
                       translation TEXT,
                       translation_length INTEGER)''')
    conn.commit()
    return conn, cursor

def insert_chunks(cursor, chunks):
    for chunk in chunks:
        cursor.execute('''INSERT INTO chunks (original_text, length, translation)
                          VALUES (?, ?, ?)''', (chunk, len(chunk), None))

def translate_text(text):
    encoding_name = "cl100k_base"  # GPT-4에 적합한 인코딩
    max_tokens = 64000  # 안전한 최대 토큰 수

    # 토큰 수 계산 및 제한
    total_tokens = num_tokens_from_string(text, encoding_name)
    if total_tokens > max_tokens:
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(text)
        truncated_tokens = tokens[:max_tokens]
        text = encoding.decode(truncated_tokens)
        print(f"입력 텍스트가 {total_tokens} 토큰으로 최대 길이를 초과하여 {max_tokens} 토큰으로 잘렸습니다.")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a translator. Translate the given text from English to Korean. Do not provide any additional explanation other than the translation."},
            {"role": "user", "content": f"Translate the following text to Korean: {text}"}
        ]
    )
    return response.choices[0].message.content.strip()

def update_translations(conn, cursor):
    cursor.execute("SELECT id, original_text FROM chunks WHERE translation IS NULL")
    rows = cursor.fetchall()

    for row in rows:
        id, original_text = row
        translated = translate_text(original_text)
        translation_length = len(translated)

        cursor.execute('''UPDATE chunks
                          SET translation = ?, translation_length = ?
                          WHERE id = ?''', (translated, translation_length, id))
        conn.commit()  # 각 번역 후 커밋
        print(f"Translated chunk {id}")

def save_translations_to_file(cursor):
    cursor.execute("SELECT translation FROM chunks")
    translations = cursor.fetchall()
    translation_text = "\n\n".join([t[0] for t in translations if t[0]])

    output_directory = "translations"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    filename = "translation_results.txt"
    file_path = os.path.join(output_directory, filename)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(translation_text)

    print(f"번역 결과가 '{file_path}'에 저장되었습니다.")

def main():
    # 첫 번째 .txt 파일 찾기
    first_txt_file = get_first_txt_file()
    if not first_txt_file:
        print("No .txt files found in the current directory.")
        return

    # 텍스트 파일 읽기
    with open(first_txt_file, 'r', encoding='utf-8') as file:
        text = file.read()

    # 줄바꿈 문자로 분리
    lines = text.split('\n')

    # 청크 생성
    chunks = []
    current_chunk = ""
    for line in lines:
        if len(current_chunk) + len(line) + 1 > 700:
            chunks.extend(create_chunks(current_chunk))
            current_chunk = line + '\n'
        else:
            current_chunk += line + '\n'

    if current_chunk:
        chunks.extend(create_chunks(current_chunk))

    # DB 생성 및 연결
    conn, cursor = create_db_and_table()

    # 청크 삽입
    insert_chunks(cursor, chunks)

    print(f"파일 '{first_txt_file}'에서 총 {len(chunks)}개의 청크가 DB에 저장되었습니다.")

    # 번역 수행
    print("번역을 시작합니다...")
    update_translations(conn, cursor)
    print("번역이 완료되었습니다.")

    # 번역 결과를 파일로 저장
    save_translations_to_file(cursor)

    # 결과 출력 (예시로 처음 5개 행)
    cursor.execute("SELECT * FROM chunks LIMIT 5")
    for row in cursor.fetchall():
        print(row)

    # 연결 종료
    conn.close()

if __name__ == "__main__":
    main()