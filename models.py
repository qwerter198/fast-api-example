
from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class UserModel(Base):
    """使用者資料表模型"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(128), nullable=False)
    role = Column(String(20), nullable=False, default="user")  # admin/user
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"

class ItemModel(Base):
    """商品資料表模型"""
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f"<Item(id={self.id}, name='{self.name}', price={self.price})>"
