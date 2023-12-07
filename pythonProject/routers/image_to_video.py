from fastapi import APIRouter
from fastapi.responses import FileResponse
from fastapi import FastAPI, File, UploadFile, HTTPException
import os
from PIL import Image
from io import BytesIO
import shutil
from fastapi.responses import StreamingResponse
from zipfile import ZipFile
import io

upload = APIRouter(prefix='/image_to_video')
send = APIRouter(prefix='/image_to_video')
send_dir = './img3d'

# 이미지를 업로드하고 저장할 디렉토리
UPLOAD_DIR = "./uploaded_images"

# def img():
#     image = Image.open(f'./uploaded_images/111.jpg')
#     return image

# 이미지 업로드를 처리하는 엔드포인트
@upload.post("/send")
async def upload_image(file: UploadFile):
    # 업로드된 이미지의 파일명을 생성 (파일명은 원래 파일명을 그대로 사용할 수도 있습니다.)
    file_name = os.path.join(UPLOAD_DIR, file.filename)
    file_path = os.path.join(UPLOAD_DIR, "tmp8nr2ywzo.mp4")
    print(file_path)
    # 이미지를 디스크에 저장
    with open(file_name, "wb") as image_file:
        image_file.write(file.file.read())

    return FileResponse(file_path, media_type="video/mp4")

@upload.get("/getvideo")
async def upload_video():
    file_path = os.path.join(UPLOAD_DIR, "tmp8nr2ywzo.mp4")
    print(file_path)
    return FileResponse(file_path, media_type="video/mp4")


def process_image_and_save(image: UploadFile):
    # 이미지를 처리하고 obj, png, mtl 파일 생성 (여기에 모델 적용 코드 추가)
    obj_path = os.path.join(send_dir, "tiger_mesh.obj")
    png_path = os.path.join(send_dir, "tiger_mesh_albedo.png")
    mtl_path = os.path.join(send_dir, "tiger_mesh.mtl")

    # 임시 파일 저장 (실제 로직에서는 모델이 파일을 생성하게 됩니다)
    with open(obj_path, "w") as f:
        f.write("obj file content")
    with open(png_path, "wb") as f:
        f.write(b"png file binary content")
    with open(mtl_path, "w") as f:
        f.write("mtl file content")

    return obj_path, png_path, mtl_path

@send.post("/send3d")
async def create_3d_model(image: UploadFile = File(...)):
    # 파일을 임시 디렉터리에 저장
    image_path = os.path.join(send_dir, image.filename)
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # 이미지를 처리하고 파일 생성
    obj_path, png_path, mtl_path = process_image_and_save(image)

    # 파일을 zip으로 압축
    zip_filename = "model_files.zip"
    zip_path = os.path.join(send_dir, zip_filename)
    with ZipFile(zip_path, 'w') as zipf:
        zipf.write(obj_path, os.path.basename(obj_path))
        zipf.write(png_path, os.path.basename(png_path))
        zipf.write(mtl_path, os.path.basename(mtl_path))

    # 압축 파일을 메모리에 로드
    zip_in_memory = io.BytesIO()
    with open(zip_path, 'rb') as zip_disk:
        zip_in_memory.write(zip_disk.read())
    zip_in_memory.seek(0)
    a = StreamingResponse(zip_in_memory, media_type="application/zip", headers={"Content-Disposition": f"attachment;filename={zip_filename}"})
    print(a)
    # 생성된 zip 파일을 클라이언트에게 전송
    return StreamingResponse(zip_in_memory, media_type="application/zip", headers={"Content-Disposition": f"attachment;filename={zip_filename}"})
