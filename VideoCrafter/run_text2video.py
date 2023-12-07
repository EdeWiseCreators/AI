import argparse
import os
from fastapi import APIRouter
from fastapi.responses import FileResponse
from fastapi import FastAPI, File, UploadFile
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image


video = APIRouter(prefix='/video_crafter')



img_path = "./img"
OUTPUT_DIR = "./static"
# 결과 폴더와 video_download 폴더의 경로 설정
results_folder = './results'
video_download_folder = './video_download'

cnt = 0
gif_name = './static'

def upload_img(img_path):

    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to("cuda")
    
    raw_image = Image.open(img_path).convert('RGB')

    inputs = processor(raw_image, return_tensors="pt").to("cuda")

    out = model.generate(**inputs)
    result = processor.decode(out[0], skip_special_tokens=True)
    
    return result

def save_text_to_file(text, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)
        
        
@video.post("/text_2_video")
def text_2_video(file: UploadFile):
    global cnt
    # global gif_name
    
    # 업로드된 이미지의 파일명을 생성 (파일명은 원래 파일명을 그대로 사용할 수도 있습니다.)
    file_name = os.path.join(img_path, file.filename)
    print(file_name)
    # 이미지를 디스크에 저장
    with open(file_name, "wb") as image_file:
        image_file.write(file.file.read())

    result = upload_img(file_name)
    print("result:::::", result)
    
    cnt += 1
    
    gif_name = f"text_2_video{cnt}"
    txt_name = f"text_2_video{cnt}.txt"
    mp4_name = f"text_2_video{cnt}.mp4"
    save_path = './results/base_1024_test'
    file_path = os.path.join(save_path, gif_name)
    txt_path = os.path.join(OUTPUT_DIR, txt_name)
    mp4_path = os.path.join(save_path, mp4_name)
    print(file_path)
    print(txt_path)
    
    user_input = 'An elk is standing in the grass.'
    # user_input = result #저장할 텍스트를 입력하세요

    save_text_to_file(user_input, txt_path)
    print(f"텍스트가 {txt_path}에 저장되었습니다.")    

    
    # text to video model start
    print("**********text to video model start*******")
    os.system(f"python3 scripts/evaluation/inference.py "
            f"--mode=base "
            f"--ckpt_path=checkpoints/base_1024_v1/model.ckpt "
            f"--config=configs/inference_t2v_1024_v1.0.yaml "
            f"--savedir='{save_path}' " 
            f"--n_samples=1 "
            f"--bs=1 "
            f"--height=576 "
            f"--width=1024 "
            f"--unconditional_guidance_scale=12.0 "
            f"--ddim_steps=50 "
            f"--ddim_eta=1.0 "
            f"--prompt_file={txt_path} "
            f"--fps=28 ")
    
    return FileResponse(mp4_path, filename=mp4_name)
    # return {"message": "Video created successfully"}









# @video.post("/text_2_video")
# def upload_video(file: UploadFile):
#     global cnt
#     global count

#     # 업로드된 이미지의 파일명을 생성 (파일명은 원래 파일명을 그대로 사용할 수도 있습니다.)
#     file_name = os.path.join(img_path, file.filename)
#     print(file_name)
#     # 이미지를 디스크에 저장
#     with open(file_name, "wb") as image_file:
#         image_file.write(file.file.read())

#     result = upload_img(file_name)
#     print("result:::::", result)
    
#     gif_name = f"text_2_video{cnt}.gif"
#     file_path = os.path.join(OUTPUT_DIR, gif_name)
#     print(file_path)
    
#     user_input = result #저장할 텍스트를 입력하세요

#     save_text_to_file(user_input, file_path)
#     print(f"텍스트가 {file_path}에 저장되었습니다.")    
    
#     cnt += 1

#     # 터미널 명령어 실행 및 결과 읽기
#     os.system(f"python scripts/evaluation/inference.py "
#               f"--mode=base "
#               f"--ckpt_path=checkpoints/base_1024_v1/model.ckpt "
#               f"--savedir='{file_path}'" 
#               f"--n_samples=1"
#               f"--bs=1"
#               f"--height=576"
#               f"--width=1024"
#               f"--unconditional_guidance_scale=12.0"
#               f"--ddim_steps=50"
#               f"--ddim_eta=1.0"
#               f"--prompt_file=prompts/test_prompts.txt"
#               f"--fps=28")

#     return FileResponse(file_path, filename=gif_name)

