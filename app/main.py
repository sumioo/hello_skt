from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.models import User, RoleEnum, StatusEnum
from app.crud import create_user, get_user, list_users, update_user_role, delete_user
from app.api_response import APIResponse, wrap_api_response

app = FastAPI()


from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    status: StatusEnum = StatusEnum.PENDING
    role: RoleEnum = RoleEnum.USER

@app.post("/users/", response_model=APIResponse[UserCreate])
async def api_create_user(name: str,
                          status: StatusEnum = StatusEnum.PENDING,
                          role: RoleEnum = RoleEnum.USER,
                          session: AsyncSession = Depends(get_session)):
    return wrap_api_response(await create_user(session, name, status, role))

@app.get("/users/{user_id}", response_model=APIResponse[User])
async def api_get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/", response_model=APIResponse[List[User]])
async def api_list_users(session: AsyncSession = Depends(get_session)):
    return wrap_api_response(await list_users(session))

@app.patch("/users/{user_id}/role", response_model=APIResponse[User])
async def api_update_role(user_id: int, role: RoleEnum,
                          session: AsyncSession = Depends(get_session)):
    user = await update_user_role(session, user_id, role)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/users/{user_id}", response_model=APIResponse[bool])
async def api_delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    success = await delete_user(session, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True}