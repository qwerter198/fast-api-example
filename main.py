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

# 模擬數據庫
items_db = [
    {"id": 1, "name": "筆記本電腦", "description": "高性能工作筆電", "price": 25000.0, "is_available": True},
    {"id": 2, "name": "無線滑鼠", "description": "人體工學設計", "price": 800.0, "is_available": True},
    {"id": 3, "name": "機械鍵盤", "description": "青軸機械鍵盤", "price": 3500.0, "is_available": False},
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
    update_data = item_update.dict(exclude_unset=True)
    
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


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
