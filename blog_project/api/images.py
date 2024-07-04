# api/images.py
from fastapi import APIRouter, UploadFile, File
from services.aws_s3_service import upload_image

router = APIRouter()

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"tmp/{file.filename}"
    with open(file_location, "wb") as buffer:
        buffer.write(file.file.read())
    image_url = upload_image(file_location)
    return {"image_url": image_url}
