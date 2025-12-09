import os
import re
import sys

TEMPLATE_DIR = "app/templates"

def fix_template(path, preview=False):
    print(f"\n🔧 수정 대상: {path}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    original = content
    fixed = content

    changed = False

    # -----------------------------
    # 1) layout.html 미상속 자동 추가
    # -----------------------------
    if "{% extends" not in fixed:
        print(" ➤ layout.html 미상속 → 자동 추가 예정")
        fixed = '{% extends "layout.html" %}\n{% block content %}\n' + fixed + '\n{% endblock %}'
        changed = True

    # -----------------------------
    # 2) block end 부족 → 자동 추가
    # -----------------------------
    open_blocks = fixed.count("{% block content %}")
    close_blocks = fixed.count("{% endblock %}")

    if open_blocks > close_blocks:
        print(" ➤ endblock 부족 → 자동 추가 예정")
        fixed += "\n{% endblock %}"
        changed = True

    # -----------------------------
    # 3) 중복 html/body 제거
    # -----------------------------
    if "<html" in fixed.lower() or "<body" in fixed.lower():
        print(" ➤ <html>/<body> 태그 제거 예정")
        fixed = re.sub(r"<\/?html[^>]*>", "", fixed, flags=re.IGNORECASE)
        fixed = re.sub(r"<\/?body[^>]*>", "", fixed, flags=re.IGNORECASE)
        changed = True

    # -----------------------------
    # PREVIEW 모드이면 미리보기만 하고 리턴
    # -----------------------------
    if preview:
        if changed:
            print(" --- 변경 미리보기 ---")
            print(fixed)
        else:
            print(" ✔ 변경 없음")
        return

    # -----------------------------
    # 4) 백업 파일 생성
    # -----------------------------
    if changed:
        backup_path = path + ".backup"
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(original)
        print(f" ✔ 백업 생성됨: {backup_path}")

        # -----------------------------
        # 5) 원본 파일 덮어쓰기
        # -----------------------------
        with open(path, "w", encoding="utf-8") as f:
            f.write(fixed)
        print(f" ✔ 수정 완료: {path}")
    else:
        print(" ✔ 변경 필요 없음")


def run(preview=False):
    print("🔍 템플릿 자동 점검 시작...\n")

    files = [f for f in os.listdir(TEMPLATE_DIR) if f.endswith(".html")]
    print("📄 검사 대상:", ", ".join(files))

    for filename in files:
        fix_template(os.path.join(TEMPLATE_DIR, filename), preview=preview)

    print("\n🎉 작업 완료!")


if __name__ == "__main__":
    preview_mode = "--preview" in sys.argv
    run(preview=preview_mode)
