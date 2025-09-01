from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import ItemModel, UserModel
from typing import List, Optional

class UserService:
    """使用者服務類，處理所有使用者相關的資料庫操作"""

    @staticmethod
    async def create_user(db: AsyncSession, username: str, hashed_password: str, role: str = "user") -> UserModel:
        new_user = UserModel(username=username, hashed_password=hashed_password, role=role)
        db.add(new_user)
        await db.flush()
        await db.refresh(new_user)
        return new_user

 # 商品服務類，處理所有商品相關的資料庫操作
class ItemService:
    @staticmethod
    async def get_all_items(db: AsyncSession) -> List[ItemModel]:
        result = await db.execute(select(ItemModel))
        return result.scalars().all()

    @staticmethod
    async def get_item_by_id(db: AsyncSession, item_id: int) -> Optional[ItemModel]:
        result = await db.execute(select(ItemModel).where(ItemModel.id == item_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_item(db: AsyncSession, name: str, description: Optional[str], price: float, is_available: bool = True) -> ItemModel:
        new_item = ItemModel(name=name, description=description, price=price, is_available=is_available)
        db.add(new_item)
        await db.flush()
        await db.refresh(new_item)
        return new_item

    @staticmethod
    async def update_item(db: AsyncSession, item_id: int, **kwargs) -> Optional[ItemModel]:
        result = await db.execute(select(ItemModel).where(ItemModel.id == item_id))
        item = result.scalar_one_or_none()
        if item is None:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(item, key):
                setattr(item, key, value)
        await db.flush()
        await db.refresh(item)
        return item

    # ...existing code...
    
    @staticmethod
    async def delete_item(db: AsyncSession, item_id: int) -> Optional[ItemModel]:
        """刪除商品"""
        result = await db.execute(select(ItemModel).where(ItemModel.id == item_id))
        item = result.scalar_one_or_none()
        
        if item is None:
            return None
        
        await db.delete(item)
        return item
