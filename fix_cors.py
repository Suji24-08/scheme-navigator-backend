content = open('app/main.py', 'r', encoding='utf-8').read()

old = '''app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your actual Vercel domain once deployed
    allow_methods=["*"],
    allow_headers=["*"],
)'''

new = '''app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://scheme-navigator-frontend.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)'''

assert content.count(old) == 1, f"Expected 1 match, found {content.count(old)}"
content = content.replace(old, new)

open('app/main.py', 'w', encoding='utf-8', newline='\n').write(content)
print("CORS locked to Vercel domain.")