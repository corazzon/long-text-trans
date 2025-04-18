from flask import Flask, render_template_string
import sqlite3

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>번역 결과 보기</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f4f4f4; }
    </style>
</head>
<body>
    <h1>번역 데이터</h1>
    <table>
        <thead>
            <tr>
                <th>원문</th>
                <th>번역</th>
            </tr>
        </thead>
        <tbody>
            {% for original, translated in translations %}
            <tr>
                <td>{{ original }}</td>
                <td>{{ translated }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

def fetch_translation_data(db_path):
    """SQLite 데이터베이스에서 번역 데이터를 가져옵니다."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT original_text, translation FROM chunks WHERE translation IS NOT NULL")
    data = cursor.fetchall()
    conn.close()
    return data

@app.route('/')
def show_translations():
    """번역 데이터가 포함된 HTML 페이지를 렌더링합니다."""
    db_path = 'text_chunks.db'
    translations = fetch_translation_data(db_path)
    return render_template_string(HTML_TEMPLATE, translations=translations)

if __name__ == '__main__':
    app.run(debug=True)