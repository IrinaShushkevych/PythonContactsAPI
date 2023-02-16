from fastapi import FastAPI
import uvicorn

from src import  router_contacts, router_auth

app = FastAPI()

app.include_router(router_auth, prefix='/api')
app.include_router(router_contacts, prefix='/api')



@app.get("/")
def main():
    return {"message": "Hello!!!"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
