import os, sys, shutil
from textual_inversion import textual_inversion as TI
import preprocess_image as PI
import torch
import subprocess
from glob import glob
from fastapi import APIRouter, Form
from typing_extensions import Annotated
from fastapi.responses import FileResponse
from fastapi import FastAPI, File, UploadFile
from PIL import Image
import threading
import zipfile
import tempfile

img23d = APIRouter(prefix='/one_click_process')
input_images = "./reference_imgs"
file_name = ""
output_3d = "./run"
output_3d_obj = "outputs/retouch/mesh/mesh.obj"
output_3d_png = "outputs/retouch/mesh/albedo.png"
class Make_3d_Modeling():
    def __init__(self, filepath, is_bool, token):
        self.filepath = filepath
        self.device = 'cuda'
        self.is_bool = is_bool
        self.token = token
        self.python_cmd = '/home/meta-ai2/anaconda3/envs/edu_magic/bin/python'

    # Step 1: 이미지 전처리
    def preprocess(self):
        # 결과물 폴더 생성
        self.new_folder = self.filepath.split('/')[-1].split('.')[0]  # ex) ./run/mask.jpg >> mask
        print('self.new_folder: ', self.new_folder)
        self.new_path = f'./run/{self.new_folder}' # 경로 설정
        print('self.new_path: ', self.new_path)
        os.makedirs(self.new_path + '/images', exist_ok=True)
        shutil.move(self.filepath, self.new_path + '/images/image.jpg')

        self.filepath = self.new_path + '/images/image.jpg'  # 이미지 경로를 파일 경로로 업데이트
        self.depth_estimator = PI.DepthEstimator()
        PI.process_single_image(self.filepath, self.depth_estimator)

        return "preprocess finished!"

    def textual_inversion(self):
        torch.cuda.empty_cache()
        if self.is_bool==True:
            self.pretrained_model = 'runwayml/stable-diffusion-v1-5'
            self.train_data_dir = self.new_path + '/images/rgba.png'
            self.learnable_property = 'object'
            self.placeholder_token = f'_{self.new_folder}_'
            self.initializer_token = f'{self.token}'
            self.resolution = 512
            self.train_batch_size = 10
            self.gradient_accumulation_steps = 1
            self.max_train_steps = 3000
            self.lr_scheduler = 'constant'
            self.lr_warmup_steps = 0
            os.makedirs(self.new_path + '/textual_inversion', exist_ok=True)
            self.output_dir = self.new_path + '/textual_inversion'

            cmd = self.python_cmd + ' textual_inversion/textual_inversion.py -O' \
                 + f' --pretrained_model_name_or_path "{self.pretrained_model}" \
                      --train_data_dir {self.train_data_dir} \
                      --learnable_property {self.learnable_property} \
                      --placeholder_token {self.placeholder_token} \
                      --initializer_token {self.initializer_token} \
                      --resolution {self.resolution} \
                      --train_batch_size {self.train_batch_size} \
                      --gradient_accumulation_steps {self.gradient_accumulation_steps} \
                      --max_train_steps {self.max_train_steps} \
                      --lr_scheduler {self.lr_scheduler} \
                      --lr_warmup_steps {self.lr_warmup_steps} \
                      --output_dir {self.output_dir} \
                      --use_augmentations'
            
            subprocess.run(cmd, shell=True)
            shutil.move(self.output_dir + '/learned_embeds.bin', self.new_path + '/images/learned_embeds.bin')
        else:
            pass

    def first_progress(self):
        torch.cuda.empty_cache()
        self.sd_version = '1.5'
        self.image = self.new_path + '/images/rgba.png'
        self.first_workspace = self.new_path + '/outputs/first'
        self.optim = 'adam'
        self.iters = 5000
        self.guidance = "SD zero123"
        self.lambda_guidance_1 = 1.0
        self.lambda_guidance_2 = 40.0
        self.guidance_scale_1 = 100.0
        self.guidance_scale_2 = 5.0
        self.latent_iter_ratio = 0.0
        self.normal_iter_ratio = 0.2
        self.t_range_1 = 0.2
        self.t_range_2 = 0.6
        self.bg_radius = -1.0
        
        if self.is_bool==True:
            self.text = "A high-resolution DSLR image of <token>"
            self.learned_embeds_path = self.new_path + '/images/learned_embeds.bin'
            cmd = self.python_cmd + ' main.py -O' \
                 + f' --text "{self.text}" \
                      --sd_version {self.sd_version} \
                      --image {self.image} \
                      --learned_embeds_path {self.learned_embeds_path} \
                      --workspace {self.first_workspace} \
                      --optim {self.optim} \
                      --iters {self.iters} \
                      --guidance {self.guidance} \
                      --lambda_guidance {self.lambda_guidance_1} {self.lambda_guidance_2} \
                      --guidance_scale {self.guidance_scale_1} {self.guidance_scale_2} \
                      --latent_iter_ratio {self.latent_iter_ratio} \
                      --normal_iter_ratio {self.normal_iter_ratio} \
                      --t_range {self.t_range_1} {self.t_range_2} \
                      --bg_radius {self.bg_radius} \
                      --save_mesh'

            subprocess.run(cmd, shell=True)
            
        else:
            self.text = f"A high-resolution DSLR image of a {self.new_folder}"
            # subprocess로 스크립트 내부에서 .py 파일 실행
            cmd = self.python_cmd + ' main.py -O' \
                 + f' --text "{self.text}" \
                      --sd_version {self.sd_version} \
                      --image {self.image} \
                      --workspace {self.first_workspace} \
                      --optim {self.optim} \
                      --iters {self.iters} \
                      --guidance {self.guidance} \
                      --lambda_guidance {self.lambda_guidance_1} {self.lambda_guidance_2} \
                      --guidance_scale {self.guidance_scale_1} {self.guidance_scale_2} \
                      --latent_iter_ratio {self.latent_iter_ratio} \
                      --normal_iter_ratio {self.normal_iter_ratio} \
                      --t_range {self.t_range_1} {self.t_range_2} \
                      --bg_radius {self.bg_radius} \
                      --save_mesh'

            subprocess.run(cmd, shell=True)

        return "first_progress finished!"

    def second_progress(self):
        torch.cuda.empty_cache()
        self.second_workspace = self.new_path + '/outputs/retouch'
        self.checkpoint = self.first_workspace + '/checkpoints/first.pth'
        self.known_view_interval = 4
        self.lambda_guidance_1 = 1e-3
        self.lambda_guidance_2 = 0.01

        if self.is_bool==True:
            self.text = "A high-resolution DSLR image of <token>"
            self.learned_embeds_path = self.new_path + '/images/learned_embeds.bin'
            cmd = self.python_cmd + ' main.py -O' \
                 + f' --text "{self.text}" \
                      --sd_version {self.sd_version} \
                      --image {self.image} \
                      --learned_embeds_path {self.learned_embeds_path} \
                      --workspace {self.second_workspace} \
                      --dmtet --init_ckpt {self.checkpoint} \
                      --optim {self.optim} \
                      --iters {self.iters} \
                      --known_view_interval {self.known_view_interval} \
                      --guidance {self.guidance} \
                      --lambda_guidance {self.lambda_guidance_1} {self.lambda_guidance_2} \
                      --guidance_scale {self.guidance_scale_1} {self.guidance_scale_2} \
                      --latent_iter_ratio {self.latent_iter_ratio} \
                      --rm_edge \
                      --bg_radius {self.bg_radius} \
                      --save_mesh'            
            
            subprocess.run(cmd, shell=True)

        else:
            self.text = f"A high-resolution DSLR image of a {self.new_folder}"
            cmd = self.python_cmd + ' main.py -O' \
                 + f' --text "{self.text}" \
                      --sd_version {self.sd_version} \
                      --image {self.image} \
                      --workspace {self.second_workspace} \
                      --dmtet --init_ckpt {self.checkpoint} \
                      --optim {self.optim} \
                      --iters {self.iters} \
                      --known_view_interval {self.known_view_interval} \
                      --guidance {self.guidance} \
                      --lambda_guidance {self.lambda_guidance_1} {self.lambda_guidance_2} \
                      --guidance_scale {self.guidance_scale_1} {self.guidance_scale_2} \
                      --latent_iter_ratio {self.latent_iter_ratio} \
                      --rm_edge \
                      --bg_radius {self.bg_radius} \
                      --save_mesh'            
            
            subprocess.run(cmd, shell=True)

        return 'second_progress finished!'
    
    def run(self):
        self.preprocess()
        self.textual_inversion()
        self.first_progress()
        self.second_progress()

        print('Process Finished!!')


@img23d.post("/send3d")
def send_3d(file:UploadFile):
    global input_images
    global file_name
    file_name = os.path.join(input_images, file.filename)

    with open(file_name, "wb") as image_file:
        image_file.write(file.file.read())
    print("image_file:: ",image_file)
    
    file_name = sorted(glob("./reference_imgs/*"))
    print("file_name :::::::::::::: ",file_name)
    # 긴 작업을 백그라운드 스레드로 이동
    threading.Thread(target=process_uploaded_images).start()

    # for i in range(len(input_images)):
    #     torch.cuda.empty_cache()
    #     device = 'cuda' if torch.cuda.is_available() else 'cpu'
    #     print(device)
    #     # is_bool = False면 textual_inversion 미사용
    #     obj = Make_3d_Modeling(filepath=input_images[i], is_bool=False, token="")
    #     obj.run()
    #     print(f"Process {input_images[i]} finished!! Left: {len(input_images) - i - 1}/{len(input_images)}")

    return "upload complete! Please wait!!"

def process_uploaded_images():
    global file_name
    for i in range(len(file_name)):
        torch.cuda.empty_cache()
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(device)
        # is_bool = False면 textual_inversion 미사용
        obj = Make_3d_Modeling(filepath=file_name[i], is_bool=False, token="")
        obj.run()
        print(f"Process {file_name[i]} finished!! Left: {len(file_name) - i - 1}/{len(file_name)}")
    return "learning end!!"


# @img23d.post("/get3d", tags=['text'])
# def get_3d(text:Annotated[str, Form()]):
#     global output_3d
#     # global file_name
#     global output_3d_obj
#     global output_3d_png
#     print("file_name2:::",file_name)

#     # 리스트에서 첫 번째 항목을 가져옵니다.
#     file_name_without_extension = text
#     dir = os.path.join(output_3d, file_name_without_extension, "outputs/retouch/mesh/")
    
#     old_file_obj= os.path.join(dir, 'mesh.obj')
#     new_file_obj = os.path.join(dir, f"{file_name_without_extension}.obj")
    
#     os.rename(old_file_obj, new_file_obj)

#     old_file_png= os.path.join(dir, 'albedo.png')
#     new_file_png = os.path.join(dir, f"{file_name_without_extension}.png")
    
#     os.rename(old_file_png, new_file_png)

#     file_obj = os.path.join(dir,f"{file_name_without_extension}.obj")
#     # 파일의 기본 이름만 추출합니다.
#     # file_name_without_extension = os.path.splitext(os.path.basename(file_name))[0]
    
#     # file_obj = os.path.join(output_3d, file_name_without_extension, output_3d_obj)
#     file_png = os.path.join(dir, f"{file_name_without_extension}.png")
#     print(file_obj)
#     print(file_png)
#     # ZIP 파일의 경로를 설정합니다.
#     zip_file_path = os.path.join(output_3d, f"{file_name_without_extension}.zip")

#     # ZIP 파일을 생성합니다.
#     with zipfile.ZipFile(zip_file_path, 'w') as zipf:
#         # 파일이 실제로 존재하는지 확인하고, ZIP 파일에 추가합니다.
#         if os.path.isfile(file_obj):
#             zipf.write(file_obj, os.path.basename(file_obj))
#         else:
#             return {"error": "OBJ File not found."}

#         if os.path.isfile(file_png):
#             zipf.write(file_png, os.path.basename(file_png))
#         else:
#             return {"error": "PNG File not found."}

#     # ZIP 파일을 응답으로 반환합니다.
#     return FileResponse(zip_file_path, media_type='application/zip', filename=f"{file_name_without_extension}.zip")