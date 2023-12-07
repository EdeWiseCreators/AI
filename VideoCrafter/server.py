from fastapi import FastAPI
import uvicorn
from run_text2video import video

app = FastAPI()
app.include_router(video)

@app.get('/')
def root():
    return {'message': "Hi"}




# uvicorn server:app --reload --host=0.0.0.0 --port=5055