import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


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

"""
upload file to S3
"""
def upload_file(location, file):
    try:
        client_s3.upload_file(
            location,
            bucket_name,
            file,
            ExtraArgs={'ContentType': 'image/jpg'}
        )

        return "Upload File"
    except Exception as e :
        print(f"Error => {e}")
        return f"Error => {e}"
    
def upload_file_gif(location, file):
    try:
        client_s3.upload_file(
            location,
            bucket_name,
            file,
            ExtraArgs={'ContentType': 'image/gif'}
        )

        return "Upload File"
    except Exception as e :
        print(f"Error => {e}")
        return f"Error => {e}"
    
def upload_file_obj(location_obj, location_png, file, file_png):
    try:
        client_s3.upload_file(
            location_obj,
            bucket_name,
            file,
            ExtraArgs={'ContentType': 'Application/octet-stream'}
        )
        client_s3.upload_file(
            location_png,
            bucket_name,
            file_png,
            ExtraArgs={'ContentType': 'image/png'}
        )

        return "Upload File"
    except Exception as e :
        print(f"Error => {e}")
        return f"Error => {e}"
    


def download_file_img(filename):
    """
    s3 : 연결된 s3 객체(boto3 client)
    filename : s3에 저장된 파일 명
    """
    KEY = filename
    FILE_PATH_FILE_NAME = FILE_PATH + "/" + KEY
    # 파일이 존재하는지 확인
    try:
        client_s3.head_object(Bucket=bucket_name, Key=KEY)
    except client_s3.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"File {KEY} not found in the S3 bucket.")
            return False
        else:
            print(f"Error checking file existence: {e}")
            return False

    # 파일 다운로드 시도
    try:
        client_s3.download_file(bucket_name, KEY, FILE_PATH_FILE_NAME)
        print("파일 다운로드")
    except NoCredentialsError:
        print("Credentials not available")
        return False
    except Exception as e:
        print(f"Error => {e}")
        print("파일 다운로드 실패")
        return False