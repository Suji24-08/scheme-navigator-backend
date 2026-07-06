content = open('app/main.py', 'r', encoding='utf-8').read()

addition = '''

@app.post("/admin/ingest-schemes")
def ingest_schemes_endpoint():
    from app.core.vectorstore import ingest_schemes
    count = ingest_schemes()
    return {"status": "ok", "documents_ingested": count}
'''

content += addition
open('app/main.py', 'w', encoding='utf-8', newline='\n').write(content)
print("Done.")