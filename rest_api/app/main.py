import uvicorn
from fastapi import FastAPI
from routes import router
from db import Base, engine


async def lifespan(app: FastAPI):
    # Startup logic
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Message Service API",
    description="A message service with both REST and gRPC interfaces",
    version="1.0.0",
)

app.include_router(router)


@app.get("/")
def index():
    return {
        "message": "Message Service API",
        "docs": "/docs",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
