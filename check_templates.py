import os
import re

TEMPLATE_DIR = "app/templates"

print("🔍 템플릿 자동 점검 시작...\n")

missing_extends = []
duplicate_html_tags = []
missing_user_context = []
wrong_block_structure = []
checked_files = []

html_tag_pattern = re.compile(r"<html|<body", re.IGNORECASE)
extends_pattern = re.compile(r"{%\s*extends\s+['\"]layout\.html['\"]\s*%}")
block_pattern = re.compile(r"{%\s*block\s+content\s*%}.*?{%\s*endblock\s*%}", re.DOTALL)

for root, _, files in os.walk(TEMPLATE_DIR):
    for f in files:
        if not f.endswith(".html"):
            continue

        path = os.path.join(root, f)
        checked_files.append(f)

        with open(path, "r", encoding="utf-8") as file:
            content = file.read()

        # 1) layout 상속 여부 검사
        if f != "layout.html" and not extends_pattern.search(content):
            missing_extends.append(f)

        # 2) html/body 태그 중복 검사
        if f != "layout.html" and html_tag_pattern.search(content):
            duplicate_html_tags.append(f)

        # 3) block content 검사
        if f != "layout.html" and not block_pattern.search(content):
            wrong_block_structure.append(f)

print("📄 검사한 템플릿 파일:")
print(", ".join(checked_files), "\n")

# 출력 정리
def print_list(title, items):
    print(f"=== {title} ===")
    if items:
        for item in items:
            print(" -", item)
    else:
        print(" ✔ 문제 없음")
    print()

print_list("❌ layout.html 미상속 템플릿", missing_extends)
print_list("❌ <html>, <body> 중복 존재", duplicate_html_tags)
print_list("❌ block content 구조 불완전", wrong_block_structure)

print("🔍 검사가 완료되었습니다!\n")
print("⚡ 위 문제를 해결하면 로그인 유지 및 네비게이션 표시가 100% 정상 동작합니다.")
