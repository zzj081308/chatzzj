import uuid
import os
from fastapi import UploadFile
from app.config import settings


async def save_upload(file: UploadFile, subfolder: str = "chat_images") -> str:
    """Save uploaded file and return relative URL path."""
    ext = os.path.splitext(file.filename or ".png")[1].lower() or ".png"
    safe_ext = ext if ext in settings.ALLOWED_FILE_EXTENSIONS else '.bin'
    filename = f"{uuid.uuid4().hex}{safe_ext}"

    upload_dir = os.path.join(settings.UPLOAD_DIR, subfolder)
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, filename)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return f"/uploads/{subfolder}/{filename}"


