from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.db import Base, engine, init_db
from app.controllers.auth_controller import router as auth_router
from app.controllers.user_controller import router as user_router
from app.core.rate_limit import limiter

app = FastAPI(title="House Price API")

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from app.controllers.prediction_controller import router as prediction_router

api = APIRouter(prefix="/api-deutsche")
api.include_router(auth_router, tags=["auth"])
api.include_router(user_router, prefix="/users", tags=["users"])
api.include_router(prediction_router, tags=["predict"])
app.include_router(api)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        reload_dirs=["app"]
    )
