from fastapi import FastAPI
from routes import note_router
from db import Base, engine
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(_app:FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(note_router, prefix="/api/notes", tags=["Notes"])

