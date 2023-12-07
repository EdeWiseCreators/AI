import uvicorn
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import local_2_s3

file_name = ''
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

IMAGE_ROOT_DIR = './'

def create_app() -> FastAPI:
    app = FastAPI()
    return app


app = create_app()


@app.get("/")
async def read_root():
    test_env = os.environ["TEST_ENV"]
    return {"result": test_env}

@app.get("/upload_s3_img")
async def upload_s3_img():
    return_message = ''
    location = "D:/10_project_aws/static/image/rabbit.jpg"
    file = "test_1.jpg"
    return_message = local_2_s3.upload_file(location, file)
    return {"result": return_message}

@app.get("/upload_s3_gif")
async def upload_s3_gif():
    return_message = ''
    location = "D:/10_project_aws/static/gif/rabbit.gif"
    file = "test_2"
    return_message = local_2_s3.upload_file_gif(location, file)
    return {"result": return_message}

@app.get("/upload_s3_obj")
async def upload_s3_obj():
    return_message = ''
    location_obj = "D:/10_project_aws/static/obj/ng_mesh.obj"
    location_png = "D:/10_project_aws/static/obj/ng_mesh_albedo.png"
    file = "obj/test_5"
    file_png = file + "_albedo"
    return_message = local_2_s3.upload_file_obj(location_obj, location_png, file, file_png)
    return {"result": return_message}

@app.post("/bring_s3_img_name")
async def download_s3_img(key: dict):
    # 여기에서 key를 사용하여 원하는 작업을 수행할 수 있습니다.
    file_name = key['key']
    print("file_name :", file_name)
    local_2_s3.download_file_img(file_name)

    local_file_path = local_2_s3.FILE_PATH + "/" + file_name
    if file_name:
        return FileResponse(path=local_file_path, filename=file_name, media_type='image/jpg')
    else:
        return {"message": "Failed to download file from S3"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")

# uvicorn main:app --reload --host 0.0.0.0
# http://127.0.0.1:8000/download_s3_img