import uvicorn
import redis.asyncio as redis
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter


from src import router_contacts, router_auth, router_users
from src.conf.config import settings

app = FastAPI()

origins = [
    "http://localhost:3000"
    ]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])

app.include_router(router_auth, prefix='/api')
app.include_router(router_contacts, prefix='/api')
app.include_router(router_users, prefix='/api')


@app.on_event('startup')
async def startup():
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db, encoding='utf-8',
                          decode_responses=True)
    await FastAPILimiter.init(r)


@app.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
def main():
    return {"message": "Hello!!!"}


if __name__ == "__main__":
    uvicorn.run(app, host=settings.main_host, port=settings.mail_port)
