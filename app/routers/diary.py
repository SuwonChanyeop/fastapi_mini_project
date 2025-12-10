from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
from app.db.session import get_db
from app.models.diary import Diary
from app.models.user import User

router = APIRouter(prefix="/diary", tags=["Diary"])

# -----------------------------
#   절대경로 템플릿 세팅
# -----------------------------
from fastapi.templating import Jinja2Templates
BASE_DIR = Path(__file__).resolve().parent.parent  # → /app
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# -----------------------------
#   일기 리스트
# -----------------------------
@router.get("/list")
def diary_list(request: Request, db: Session = Depends(get_db)):
    diaries = db.query(Diary).order_by(Diary.id.desc()).all()
    return templates.TemplateResponse("diary_list.html", {
        "request": request,
        "diaries": diaries
    })

# -----------------------------
#   일기 작성 화면
# -----------------------------
@router.get("/create")
def diary_create_page(request: Request):
    return templates.TemplateResponse("diary_create.html", {"request": request})

# -----------------------------
#   일기 작성 처리
# -----------------------------
@router.post("/create")
def diary_create(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
):

    image_path = None

    # 이미지 업로드 처리
    if file:
        static_dir = BASE_DIR / "static" / "uploads"
        static_dir.mkdir(parents=True, exist_ok=True)

        save_path = static_dir / file.filename
        with save_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        image_path = f"uploads/{file.filename}"

    diary = Diary(
        title=title,
        content=content,
        image_path=image_path,
        user_id=1,   # 로그인 기능 붙이면 수정
    )
    db.add(diary)
    db.commit()

    return RedirectResponse(url="/diary/list", status_code=303)

# -----------------------------
#   일기 상세 보기
# -----------------------------
@router.get("/detail/{diary_id}")
def diary_detail(request: Request, diary_id: int, db: Session = Depends(get_db)):
    diary = db.query(Diary).filter(Diary.id == diary_id).first()
    if not diary:
        return templates.TemplateResponse("diary_detail.html", {"request": request, "diary": None})

    return templates.TemplateResponse("diary_detail.html", {
        "request": request,
        "diary": diary
    })

# -----------------------------
#   일기 수정 화면
# -----------------------------
@router.get("/edit/{diary_id}")
def diary_edit_page(request: Request, diary_id: int, db: Session = Depends(get_db)):
    diary = db.query(Diary).filter(Diary.id == diary_id).first()
    return templates.TemplateResponse("diary_edit.html", {
        "request": request,
        "diary": diary
    })


# -----------------------------
#   일기 수정 처리
# -----------------------------
@router.post("/edit/{diary_id}")
def diary_edit(
    request: Request,
    diary_id: int,
    title: str = Form(...),
    content: str = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
):

    diary = db.query(Diary).filter(Diary.id == diary_id).first()

    # 이미지 업로드
    if file:
        static_dir = BASE_DIR / "static" / "uploads"
        static_dir.mkdir(parents=True, exist_ok=True)

        save_path = static_dir / file.filename
        with save_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        diary.image_path = f"uploads/{file.filename}"

    diary.title = title
    diary.content = content
    db.commit()

    return RedirectResponse(url=f"/diary/detail/{diary_id}", status_code=303)


# -----------------------------
#   일기 삭제
# -----------------------------
@router.get("/delete/{diary_id}")
def diary_delete(request: Request, diary_id: int, db: Session = Depends(get_db)):
    diary = db.query(Diary).filter(Diary.id == diary_id).first()

    if diary:
        db.delete(diary)
        db.commit()

    return RedirectResponse(url="/diary/list", status_code=303)

