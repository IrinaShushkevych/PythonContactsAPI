from fastapi import FastAPI
import uvicorn

from src import  router

app = FastAPI()

app.include_router(router, prefix='/api')


@app.get("/")
def main():
    return {"message": "Hello!!!"}

