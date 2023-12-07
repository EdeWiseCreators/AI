from fastapi import FastAPI
import uvicorn
from routers.chat import chatbot
from routers.image_to_video import send

app = FastAPI()
app.include_router(chatbot)
app.include_router(send)

@app.get('/')
def root():
    return {'message': "Hi"}



# gunicorn -w 30 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5056 --timeout 60 main:app --reload