import sys
import os
# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from fastapi import APIRouter
from fastapi.responses import FileResponse
from fastapi import FastAPI, File, UploadFile
from PIL import Image
from io import BytesIO
import requests
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

# Specify the local file path to your image
from dotenv import load_dotenv
import boto3
from botocore.exceptions import NoCredentialsError


# 현재 스크립트의 상위 폴더 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# .env 파일의 경로
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")

# .env 파일 로드
load_dotenv(ENV_PATH)

access_key = os.environ["access_key"]
secret_key = os.environ["secret_key"]
bucket_name = os.environ["bucket_name"]

FILE_PATH  = './tmp'

"""
connect to S3
"""
client_s3 = boto3.client(
    's3',
    aws_access_key_id = access_key,
    aws_secret_access_key = secret_key
)


img_path = "./img"

cnt = 0
count = 0
status_count = 0
local_file_path = ''
file_name = ''

def upload_img(img_path):

    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to("cuda")
    
    raw_image = Image.open(img_path).convert('RGB')

    inputs = processor(raw_image, return_tensors="pt").to("cuda")

    out = model.generate(**inputs)
    result = processor.decode(out[0], skip_special_tokens=True)
    
    return result

OUTPUT_DIR = "./static"
SAVE_DIR = "./tmp"

video = APIRouter(prefix='/text_2_video')

# @video.get("/sendvideo")
# def upload_video():
    
#     # 터미널 명령어 실행 및 결과 읽기
#     os.system("python Hotshot-XL/inference.py --prompt='squirrel climbing a tree'")
    

#     file_path = os.path.join(OUTPUT_DIR, "ttttttttttttttt.gif")
  
#     return FileResponse(file_path, media_type="image/gif")


@video.post("/sendvideo")
def upload_video(file: UploadFile):
    global cnt
    global count

    # 업로드된 이미지의 파일명을 생성 (파일명은 원래 파일명을 그대로 사용할 수도 있습니다.)
    file_name = os.path.join(img_path, file.filename)
    print(file_name)
    ######## file_path = os.path.join(img_path, "img.jpg")
    ######## print(file_path)
    ######## 이미지를 디스크에 저장
    # with open(file_name, "wb") as image_file:
    #     image_file.write(file.file.read())

    # result = upload_img(file_name)
    result = "An eagle is sitting on a tree."
    print("result:::::", result)
    ani = ", animation"
    people = "people"
    person = "person"
    men = "men"
    human = "human"
    children = "children"
    kid = "kid"
    kids = "kids"
    gif_name = f"text_2_video{cnt}.gif"
    file_path = os.path.join(OUTPUT_DIR, gif_name)
    # new_file_path = check_and_create_unique_file(file_path)
    print("file_path::::::::::::",file_path)
    print("gif_name::::::::::::",gif_name)
    cnt += 1

    if people in result or person in result or men in result or human in result or children in result or kid in result or kids in result:
        # 터미널 명령어 실행 및 결과 읽기
        os.system(f"python Hotshot-XL/inference.py --prompt=\'{result+ani}\' --output=\'{file_path}\'")
    else:
        os.system(f"python Hotshot-XL/inference.py --prompt=\'{result}\' --output=\'{file_path}\'")
    

    # upload_file_gif(file_path, gif_name)
    # count = count_files_in_folder(SAVE_DIR)
    # return "create video"
    return FileResponse(file_path, filename=gif_name)




# def upload_file_gif(location, file):
#     try:
#         client_s3.upload_file(
#             location,
#             bucket_name,
#             file,
#             ExtraArgs={'ContentType': 'image/gif'}
#         )

#         return "Upload File"
#     except Exception as e :
#         print(f"Error => {e}")
#         return f"Error => {e}"


# def download_file_img(filename):
#     """
#     s3 : 연결된 s3 객체(boto3 client)
#     filename : s3에 저장된 파일 명
#     """
#     KEY = filename
#     FILE_PATH_FILE_NAME = FILE_PATH + "/" + KEY
#     # 파일이 존재하는지 확인
#     try:
#         client_s3.head_object(Bucket=bucket_name, Key=KEY)
#     except client_s3.exceptions.ClientError as e:
#         if e.response['Error']['Code'] == '404':
#             print(f"File {KEY} not found in the S3 bucket.")
#             return False
#         else:
#             print(f"Error checking file existence: {e}")
#             return False

#     # 파일 다운로드 시도
#     try:
#         client_s3.download_file(bucket_name, KEY, FILE_PATH_FILE_NAME)
#         print("파일 다운로드")
#     except NoCredentialsError:
#         print("Credentials not available")
#         return False
#     except Exception as e:
#         print(f"Error => {e}")
#         print("파일 다운로드 실패")
#         return False

# @video.post("/bring_s3_img_name")
# async def download_s3_img(key: dict):
#     global local_file_path
#     global file_name
#     file_name = key['key']
#     print("file_name :", file_name)
#     download_file_img(file_name)

#     local_file_path = FILE_PATH + "/" + file_name
#     if file_name:
#         # return FileResponse(path=local_file_path, filename=file_name, media_type='image/jpg')
#         return "finish"
#     else:
#         return {"message": "Failed to download file from S3"}
    



# @video.get("/api/video_status")
# async def read_video_status():
#     global count
#     global status_count
#     global local_file_path
#     global file_name
#     status = ''
#     status_count = count_files_in_folder(SAVE_DIR)
#     if count == status_count:
#         status = "processing"
#         return status
#     elif count < status_count:
#         status = "complete"
#         print("file_name:",file_name)
#         print(status)
#         print("local_file_path::::::",local_file_path)
#         print("type::::::" , FileResponse(path=local_file_path, media_type='image/gif'))
#         return FileResponse(path=local_file_path, media_type='image/gif')
#     else:
#         return "error"
    

# def count_files_in_folder(folder_path):
#     count = 0
#     for root, dirs, files in os.walk(folder_path):
#         count += len(files)
#     return count