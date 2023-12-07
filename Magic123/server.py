from fastapi import FastAPI
import uvicorn
from one_click_process import img23d

app = FastAPI()
app.include_router(img23d)

@app.get('/')
def root():
    return {'message': "Hi"}

# uvicorn server:app --reload --host=0.0.0.0 --port=5054