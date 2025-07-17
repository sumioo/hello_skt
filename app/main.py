from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from .database import init_db, get_session
from .models import User, RoleEnum, StatusEnum
from .crud import create_user, get_user, list_users, update_user_role, delete_user
from contextlib import asynccontextmanager

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/users/", response_model=User)
async def api_create_user(name: str,
                          status: StatusEnum = StatusEnum.PENDING,
                          role: RoleEnum = RoleEnum.USER,
                          session: AsyncSession = Depends(get_session)):
    return await create_user(session, name, status, role)

@app.get("/users/{user_id}", response_model=User)
async def api_get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/", response_model=List[User])
async def api_list_users(session: AsyncSession = Depends(get_session)):
    return await list_users(session)

@app.patch("/users/{user_id}/role", response_model=User)
async def api_update_role(user_id: int, role: RoleEnum,
                          session: AsyncSession = Depends(get_session)):
    user = await update_user_role(session, user_id, role)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/users/{user_id}")
async def api_delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    success = await delete_user(session, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True}