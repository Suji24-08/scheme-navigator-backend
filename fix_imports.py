content = open('app/main.py', 'r', encoding='utf-8').read()

old = "from typing import Optional\n\nfrom fastapi import FastAPI\nfrom fastapi.middleware.cors import CORSMiddleware"
new = "import os\nfrom typing import Optional\n\nfrom fastapi import FastAPI, Header, HTTPException\nfrom fastapi.middleware.cors import CORSMiddleware"

assert content.count(old) == 1, f"Expected 1 match, found {content.count(old)}"
content = content.replace(old, new)

open('app/main.py', 'w', encoding='utf-8', newline='\n').write(content)
print("Imports updated.")