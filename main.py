from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# 創建 FastAPI 應用實例
app = FastAPI(
    title="FastAPI 示例應用",
    description="這是一個基本的 FastAPI 模板",
    version="1.0.0"
)

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic 模型定義
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool = True

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool = True

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_available: Optional[bool] = None

# User Pydantic 模型定義
class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    age: Optional[int] = None
    is_active: bool = True

class UserCreate(BaseModel):
    name: str
    email: str
    age: Optional[int] = None
    is_active: bool = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    is_active: Optional[bool] = None

# 模擬數據庫
items_db = [
    {"id": 1, "name": "筆記本電腦", "description": "高性能工作筆電", "price": 25000.0, "is_available": True},
    {"id": 2, "name": "無線滑鼠", "description": "人體工學設計", "price": 800.0, "is_available": True},
    {"id": 3, "name": "機械鍵盤", "description": "青軸機械鍵盤", "price": 3500.0, "is_available": False},
]

# 用戶模擬數據庫
users_db = [
    {"id": 1, "name": "張小明", "email": "ming@example.com", "age": 28, "is_active": True},
    {"id": 2, "name": "李小華", "email": "hua@example.com", "age": 32, "is_active": True},
    {"id": 3, "name": "王小美", "email": "mei@example.com", "age": 25, "is_active": False},
]

# API 路由

@app.get("/")
async def root():
    """根路由 - API 歡迎頁面"""
    return {"message": "歡迎使用 FastAPI!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "message": "服務運行正常"}

@app.get("/items", response_model=List[Item])
async def get_items():
    """獲取所有商品"""
    return items_db

@app.post("/items", response_model=Item, status_code=201)
async def create_item(item: ItemCreate):
    """創建新商品"""
    # 生成新的 ID
    new_id = max([item["id"] for item in items_db], default=0) + 1
    
    new_item = {
        "id": new_id,
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "is_available": item.is_available
    }
    
    items_db.append(new_item)
    return new_item

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item_update: ItemUpdate):
    """更新商品信息"""
    item_index = next((index for index, item in enumerate(items_db) if item["id"] == item_id), None)
    
    if item_index is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 更新商品信息
    stored_item = items_db[item_index]
    update_data = item_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        stored_item[field] = value
    
    return stored_item

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """刪除商品"""
    item_index = next((index for index, item in enumerate(items_db) if item["id"] == item_id), None)
    
    if item_index is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    deleted_item = items_db.pop(item_index)
    return {"message": f"商品 '{deleted_item['name']}' 已成功刪除"}

# 用戶管理 API 路由

@app.get("/users", response_model=List[User])
async def get_users():
    """獲取所有用戶"""
    return users_db

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """獲取特定用戶"""
    user = next((user for user in users_db if user["id"] == user_id), None)
    
    if user is None:
        raise HTTPException(status_code=404, detail="用戶不存在")
    
    return user

@app.post("/users", response_model=User, status_code=201)
async def create_user(user: UserCreate):
    """創建新用戶"""
    # 檢查郵箱是否已存在
    if any(existing_user["email"] == user.email for existing_user in users_db):
        raise HTTPException(status_code=400, detail="郵箱已存在")
    
    # 生成新的 ID
    new_id = max([user["id"] for user in users_db], default=0) + 1
    
    new_user = {
        "id": new_id,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "is_active": user.is_active
    }
    
    users_db.append(new_user)
    return new_user

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user_update: UserUpdate):
    """更新用戶信息"""
    user_index = next((index for index, user in enumerate(users_db) if user["id"] == user_id), None)
    
    if user_index is None:
        raise HTTPException(status_code=404, detail="用戶不存在")
    
    # 如果要更新郵箱，檢查是否已被其他用戶使用
    if user_update.email:
        if any(user["email"] == user_update.email and user["id"] != user_id for user in users_db):
            raise HTTPException(status_code=400, detail="郵箱已被其他用戶使用")
    
    # 更新用戶信息
    stored_user = users_db[user_index]
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        stored_user[field] = value
    
    return stored_user

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """刪除用戶"""
    user_index = next((index for index, user in enumerate(users_db) if user["id"] == user_id), None)
    
    if user_index is None:
        raise HTTPException(status_code=404, detail="用戶不存在")
    
    deleted_user = users_db.pop(user_index)
    return {"message": f"用戶 '{deleted_user['name']}' 已成功刪除"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
