content = open('app/main.py', 'r', encoding='utf-8').read()

old = '''@app.post("/admin/ingest-schemes")
def ingest_schemes_endpoint():
    from app.core.vectorstore import ingest_schemes
    count = ingest_schemes()
    return {"status": "ok", "documents_ingested": count}'''

new = '''@app.post("/admin/ingest-schemes")
def ingest_schemes_endpoint(x_admin_secret: str = Header(None)):
    if x_admin_secret != os.environ.get("ADMIN_SECRET"):
        raise HTTPException(status_code=403, detail="Forbidden")
    from app.core.vectorstore import ingest_schemes
    count = ingest_schemes()
    return {"status": "ok", "documents_ingested": count}'''

assert content.count(old) == 1, f"Expected 1 match, found {content.count(old)}"
content = content.replace(old, new)

open('app/main.py', 'w', encoding='utf-8', newline='\n').write(content)
print("Endpoint secured.")