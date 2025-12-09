from fastapi import APIRouter, Request, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime
import shutil
import os

from app.db.session import get_db
from app.repositories.user_repo import get_user_by_email, create_user, get_user_by_id
from app.core.security import verify_password, hash_password, create_access_token
from app.core.config import settings
from app.models.diary import Diary
from app.models.comment import Comment

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


# ---------------------------------------------------
# 로그인 사용자 정보
# ---------------------------------------------------
def get_logged_in_user(request: Request, db: Session):
    token = request.cookies.get("access_token")
    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = int(payload.get("sub"))
    except JWTError:
        return None

    return get_user_by_id(db, user_id)


# ---------------------------------------------------
# ⭐ 홈 화면 (명언 완전 제거)
# ---------------------------------------------------
@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    user = get_logged_in_user(request, db)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user
            # 🔥 명언 관련 코드 전부 제거
        }
    )


# ---------------------------------------------------
# 로그인 화면
# ---------------------------------------------------
@router.get("/auth/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth_login.html", {"request": request})


# ---------------------------------------------------
# 로그인 처리
# ---------------------------------------------------
@router.post("/auth/login")
async def login_submit(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, email)

    if not user or not verify_password(password, user.password):
        return RedirectResponse("/auth/login", status_code=302)

    token = create_access_token(str(user.id))

    response = RedirectResponse("/", status_code=302)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax"
    )
    return response


# ---------------------------------------------------
# 로그아웃
# ---------------------------------------------------
@router.get("/auth/logout")
async def logout():
    res = RedirectResponse("/", status_code=302)
    res.delete_cookie("access_token")
    return res


# ---------------------------------------------------
# 회원가입 화면
# ---------------------------------------------------
@router.get("/auth/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("auth_signup.html", {"request": request})


# ---------------------------------------------------
# 회원가입 처리
# ---------------------------------------------------
@router.post("/auth/signup")
async def signup_submit(
    email: str = Form(...),
    password: str = Form(...),
    nickname: str = Form(None),
    name: str = Form(None),
    phone: str = Form(None),
    db: Session = Depends(get_db),
):
    if get_user_by_email(db, email):
        return RedirectResponse("/auth/signup", status_code=302)

    hashed_pw = hash_password(password)

    create_user(
        db=db,
        email=email,
        password=hashed_pw,
        nickname=nickname,
        name=name,
        phone=phone,
    )

    return RedirectResponse("/auth/signup/success", status_code=302)


# ---------------------------------------------------
# 회원가입 완료
# ---------------------------------------------------
@router.get("/auth/signup/success", response_class=HTMLResponse)
async def signup_success(request: Request):
    return templates.TemplateResponse("auth_signup_success.html", {"request": request})


# ---------------------------------------------------
# 일기 리스트
# ---------------------------------------------------
@router.get("/diary/list", response_class=HTMLResponse)
async def diary_list(request: Request, page: int = 1, db: Session = Depends(get_db)):
    user = get_logged_in_user(request, db)

    PAGE_SIZE = 5
    total = db.query(Diary).count()
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE

    diaries = (
        db.query(Diary)
        .order_by(Diary.created_at.desc())
        .offset((page - 1) * PAGE_SIZE)
        .limit(PAGE_SIZE)
        .all()
    )

    return templates.TemplateResponse(
        "diary_list.html",
        {
            "request": request,
            "user": user,
            "diaries": diaries,
            "page": page,
            "total_pages": total_pages,
        }
    )


# ---------------------------------------------------
# 일기 작성 화면
# ---------------------------------------------------
@router.get("/diary/create", response_class=HTMLResponse)
async def diary_create_page(request: Request, db: Session = Depends(get_db)):
    user = get_logged_in_user(request, db)
    return templates.TemplateResponse("diary_create.html", {"request": request, "user": user})


# ---------------------------------------------------
# 일기 작성 처리
# ---------------------------------------------------
@router.post("/diary/create")
async def diary_create(
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    request: Request = None,
):
    user = get_logged_in_user(request, db)
    if not user:
        return RedirectResponse("/auth/login", status_code=302)

    image_path = None

    if image is not None and image.filename:
        save_dir = "app/static/images"
        os.makedirs(save_dir, exist_ok=True)

        filename = image.filename
        file_path = os.path.join(save_dir, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        image_path = f"/static/images/{filename}"

    diary = Diary(
        user_id=user.id,
        title=title,
        content=content,
        image_path=image_path,
        created_at=datetime.utcnow(),
    )

    db.add(diary)
    db.commit()

    return RedirectResponse("/diary/list", status_code=302)



# ---------------------------------------------------
# 일기 상세
# ---------------------------------------------------
@router.get("/diary/{diary_id}", response_class=HTMLResponse)
async def diary_detail(request: Request, diary_id: int, db: Session = Depends(get_db)):
    user = get_logged_in_user(request, db)
    diary = db.query(Diary).filter(Diary.id == diary_id).first()

    comments = (
        db.query(Comment)
        .filter(Comment.diary_id == diary_id)
        .order_by(Comment.created_at.asc())
        .all()
    )

    return templates.TemplateResponse(
        "diary_detail.html",
        {"request": request, "user": user, "diary": diary, "comments": comments},
    )

# ---------------------------------------------------
# 일기 수정 화면
# ---------------------------------------------------
@router.get("/diary/{diary_id}/edit", response_class=HTMLResponse)
async def diary_edit_page(request: Request, diary_id: int, db: Session = Depends(get_db)):
    user = get_logged_in_user(request, db)
    diary = db.query(Diary).filter(Diary.id == diary_id).first()

    if not diary:
        return RedirectResponse("/diary/list", status_code=302)

    # 본인 글만 수정 가능
    if not user or diary.user_id != user.id:
        return RedirectResponse("/diary/list", status_code=302)

    return templates.TemplateResponse(
        "diary_edit.html",
        {
            "request": request,
            "user": user,
            "diary": diary,
        }
    )


# ---------------------------------------------------
# 일기 수정 처리
# ---------------------------------------------------
@router.post("/diary/{diary_id}/edit")
async def diary_edit(
    diary_id: int,
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    request: Request = None,
):
    user = get_logged_in_user(request, db)
    diary = db.query(Diary).filter(Diary.id == diary_id).first()

    if not diary:
        return RedirectResponse("/diary/list", status_code=302)

    if not user or diary.user_id != user.id:
        return RedirectResponse("/diary/list", status_code=302)

    diary.title = title
    diary.content = content

    if image is not None and image.filename:
        save_dir = "app/static/images"
        os.makedirs(save_dir, exist_ok=True)

        filename = image.filename
        file_path = os.path.join(save_dir, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        diary.image_path = f"/static/images/{filename}"

    db.add(diary)
    db.commit()

    return RedirectResponse(f"/diary/{diary_id}", status_code=302)


# ---------------------------------------------------
# 일기 삭제
# ---------------------------------------------------
@router.post("/diary/{diary_id}/delete")
async def diary_delete(
    diary_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    user = get_logged_in_user(request, db)
    diary = db.query(Diary).filter(Diary.id == diary_id).first()

    if not diary:
        return RedirectResponse("/diary/list", status_code=302)

    if not user or diary.user_id != user.id:
        return RedirectResponse("/diary/list", status_code=302)

    db.query(Comment).filter(Comment.diary_id == diary_id).delete()

    db.delete(diary)
    db.commit()

    return RedirectResponse("/diary/list", status_code=302)
