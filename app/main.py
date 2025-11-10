from fastapi import FastAPI, APIRouter
from app.core.db import Base, engine
from app.controllers.auth_controller import router as auth_router
from app.controllers.user_controller import router as user_router

app = FastAPI(title="House Price API")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        reload_dirs=["app"]
    )

api = APIRouter(prefix="/api-deutsche")
api.include_router(auth_router, prefix="/auth", tags=["auth"])
api.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(api)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}
