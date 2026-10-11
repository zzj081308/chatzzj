from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.config import settings
from app.utils.file_storage import save_upload

router = APIRouter(prefix="/api/v1/upload", tags=["upload"])


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    # Validate content type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {', '.join(settings.ALLOWED_IMAGE_TYPES)}",
        )

    # Validate size
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE // (1024*1024)} MB")

    # Reset file pointer and save
    await file.seek(0)
    image_url = await save_upload(file, subfolder="chat_images")
    return {"image_url": image_url}


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Validate content type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {', '.join(settings.ALLOWED_IMAGE_TYPES)}",
        )

    # Validate size
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE // (1024*1024)} MB")

    # Reset file pointer and save
    await file.seek(0)
    avatar_url = await save_upload(file, subfolder="avatars")

    # Update user's avatar_url in database
    current_user.avatar_url = avatar_url
    await db.commit()

    return {"avatar_url": avatar_url}

@router.post("/file")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    # Validate file extension
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else ""
    if ext not in settings.ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(settings.ALLOWED_FILE_EXTENSIONS)}",
        )

    # Validate size
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Max size: {settings.MAX_FILE_SIZE // (1024*1024)} MB")

    # Reset file pointer and save
    await file.seek(0)
    file_url = await save_upload(file, subfolder="chat_files")
    return {"file_url": file_url, "file_name": file.filename}

