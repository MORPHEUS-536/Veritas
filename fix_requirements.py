import os

files_to_fix = [
    r"c:\Users\PRAVEEN RAJA\OneDrive\Desktop\Backend\Veritas\staffstuddash\backend\requirements.txt",
    r"c:\Users\PRAVEEN RAJA\OneDrive\Desktop\Backend\Veritas\dropout\requirements.txt",
]

content_staffstuddash = """fastapi
pydantic
groq
python-dotenv
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
"""

content_dropout = """fastapi
uvicorn
pydantic
python-dotenv
pandas
numpy
scikit-learn
groq
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
"""

files = {
    files_to_fix[0]: content_staffstuddash,
    files_to_fix[1]: content_dropout,
}

for filepath, content in files.items():
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"[OK] Fixed: {filepath}")
    except Exception as e:
        print(f"[ERROR] {filepath}: {e}")
