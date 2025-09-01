from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# SQLite 資料庫 URL
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# 創建異步資料庫引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # 在開發時顯示 SQL 查詢，生產環境可設為 False
    future=True
)

# 創建異步 Session 工廠
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 創建基礎模型類
Base = declarative_base()

# 依賴注入函數，用於獲取資料庫會話
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# 初始化資料庫表格
async def init_db():
    async with engine.begin() as conn:
        # 創建所有表格
        await conn.run_sync(Base.metadata.create_all)
