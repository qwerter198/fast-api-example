from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import List, Optional
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, init_db
from services import ItemService, UserService
from pydantic import BaseModel

# 權限驗證依賴
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token 驗證失敗")
    user = await UserService.get_user_by_id(db, payload["user_id"])
    if not user:
        raise HTTPException(status_code=401, detail="使用者不存在")
    return user

def require_role(role: str):
    async def role_checker(current_user=Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(status_code=403, detail="權限不足")
        return current_user
    return role_checker
from fastapi.middleware.cors import CORSMiddleware
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import List, Optional
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, init_db
from services import ItemService, UserService
from pydantic import BaseModel

# 創建 FastAPI 應用實例
app = FastAPI(
    title="FastAPI 示例應用",
    description="這是一個基本的 FastAPI 模板，使用 SQLite 資料庫",
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

# 應用啟動事件
@app.on_event("startup")
async def startup_event():
    """應用啟動時初始化資料庫"""
    await init_db()
    print("資料庫初始化完成")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your_secret_key"  # 請改為安全的隨機字串
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Pydantic 模型定義
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"  # 預設為 user

class UserUpdate(BaseModel):
    password: Optional[str] = None
    role: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

@app.post("/login", response_model=Token)
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await UserService.get_user_by_username(db, user.username)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    token_data = {"sub": db_user.username, "role": db_user.role, "user_id": db_user.id}
    access_token = create_access_token(token_data)
    return Token(access_token=access_token)
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

# 模擬數據庫 - 已移除，現在使用實際的 SQLite 資料庫
# items_db = [
#     {"id": 1, "name": "筆記本電腦", "description": "高性能工作筆電", "price": 25000.0, "is_available": True},
#     {"id": 2, "name": "無線滑鼠", "description": "人體工學設計", "price": 800.0, "is_available": True},
#     {"id": 3, "name": "機械鍵盤", "description": "青軸機械鍵盤", "price": 3500.0, "is_available": False},
# ]


from typing import Any

# User 註冊 API

# 只有 admin 可查詢所有使用者
@app.get("/users", response_model=List[UserOut])
async def get_users(db: AsyncSession = Depends(get_db), current_user=Depends(require_role("admin"))):
    users = await UserService.get_all_users(db)
    return [UserOut(id=u.id, username=u.username, role=u.role) for u in users]

@app.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="使用者不存在")
    return UserOut(id=user.id, username=user.username, role=user.role)

@app.put("/users/{user_id}", response_model=UserOut)
async def update_user(user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_db)):
    update_data = user.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))
    updated_user = await UserService.update_user(db, user_id, **update_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="使用者不存在")
    await db.commit()
    return UserOut(id=updated_user.id, username=updated_user.username, role=updated_user.role)

@app.delete("/users/{user_id}", response_model=Any)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    deleted_user = await UserService.delete_user(db, user_id)
    if not deleted_user:
        raise HTTPException(status_code=404, detail="使用者不存在")
    await db.commit()
    return {"message": "使用者已刪除"}
@app.post("/users", response_model=UserOut)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # 檢查 username 是否已存在
    exist_user = await UserService.get_user_by_username(db, user.username)
    if exist_user:
        raise HTTPException(status_code=400, detail="使用者名稱已存在")
    hashed_pw = hash_password(user.password)
    new_user = await UserService.create_user(db, user.username, hashed_pw, user.role)
    await db.commit()
    return UserOut(id=new_user.id, username=new_user.username, role=new_user.role)

@app.get("/")
async def root():
    """根路由 - API 歡迎頁面"""
    return {"message": "歡迎使用 FastAPI!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "message": "服務運行正常"}

@app.get("/items", response_model=List[Item])
async def get_items(db: AsyncSession = Depends(get_db)):
    """獲取所有商品"""
    items = await ItemService.get_all_items(db)
    return [
        Item(
            id=item.id,
            name=item.name,
            description=item.description,
            price=item.price,
            is_available=item.is_available
        )
        for item in items
    ]

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """根據 ID 獲取單個商品"""
    item = await ItemService.get_item_by_id(db, item_id)
    
    if item is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    return Item(
        id=item.id,
        name=item.name,
        description=item.description,
        price=item.price,
        is_available=item.is_available
    )

@app.post("/items", response_model=Item, status_code=201)
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    """創建新商品"""
    new_item = await ItemService.create_item(
        db=db,
        name=item.name,
        description=item.description,
        price=item.price,
        is_available=item.is_available
    )
    
    return Item(
        id=new_item.id,
        name=new_item.name,
        description=new_item.description,
        price=new_item.price,
        is_available=new_item.is_available
    )

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item_update: ItemUpdate, db: AsyncSession = Depends(get_db)):
    """更新商品信息"""
    updated_item = await ItemService.update_item(
        db=db,
        item_id=item_id,
        name=item_update.name,
        description=item_update.description,
        price=item_update.price,
        is_available=item_update.is_available
    )
    
    if updated_item is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    return Item(
        id=updated_item.id,
        name=updated_item.name,
        description=updated_item.description,
        price=updated_item.price,
        is_available=updated_item.is_available
    )

@app.delete("/items/{item_id}")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """刪除商品"""
    deleted_item = await ItemService.delete_item(db, item_id)
    
    if deleted_item is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    return {"message": f"商品 '{deleted_item.name}' 已成功刪除"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
