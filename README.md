# FastAPI 示例應用

這是一個基本的 FastAPI 應用程式模板，展示了常用的 API 功能。

## 功能特點

- ✅ RESTful API 設計
- ✅ Pydantic 數據驗證
- ✅ CORS 支持
- ✅ 自動 API 文檔生成
- ✅ 錯誤處理
- ✅ 健康檢查端點
- ✅ CRUD 操作示例

## 安裝依賴

```bash
pip install -r requirements.txt
```

## 運行應用

```bash
python main.py
```

或者使用 uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API 端點

應用運行後，可以訪問以下端點：

### 基本端點
- `GET /` - 歡迎頁面
- `GET /health` - 健康檢查

### 商品管理 API
- `GET /items` - 獲取所有商品
- `GET /items/{item_id}` - 獲取單個商品
- `POST /items` - 創建新商品
- `PUT /items/{item_id}` - 更新商品
- `DELETE /items/{item_id}` - 刪除商品
- `GET /items/search/{keyword}` - 搜索商品

### 用戶管理 API
- `GET /users` - 獲取所有用戶
- `GET /users/{user_id}` - 獲取單個用戶
- `POST /users` - 創建新用戶
- `PUT /users/{user_id}` - 更新用戶
- `DELETE /users/{user_id}` - 刪除用戶
- `GET /users/search/{keyword}` - 搜索用戶

## API 文檔

啟動應用後，可以訪問自動生成的 API 文檔：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 示例請求

### 創建商品
```bash
curl -X POST "http://localhost:8000/items" \
-H "Content-Type: application/json" \
-d '{
    "name": "新商品",
    "description": "這是一個測試商品",
    "price": 99.99,
    "is_available": true
}'
```

### 獲取所有商品
```bash
curl -X GET "http://localhost:8000/items"
```

### 搜索商品
```bash
curl -X GET "http://localhost:8000/items/search/筆記本"
```

### 創建用戶
```bash
curl -X POST "http://localhost:8000/users" \
-H "Content-Type: application/json" \
-d '{
    "name": "新用戶",
    "email": "newuser@example.com",
    "age": 25,
    "is_active": true
}'
```

### 獲取所有用戶
```bash
curl -X GET "http://localhost:8000/users"
```

### 搜索用戶
```bash
curl -X GET "http://localhost:8000/users/search/張"
```

## 項目結構

```
fast-api-example/
├── main.py              # 主應用文件
├── requirements.txt     # Python 依賴
├── README.md           # 項目說明
└── .env.example        # 環境變量示例
```

## 開發建議

1. **環境管理**: 建議使用虛擬環境
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   pip install -r requirements.txt
   ```

2. **代碼組織**: 對於大型項目，建議將代碼分離到不同模塊：
   - `models/` - Pydantic 模型
   - `routers/` - API 路由
   - `services/` - 業務邏輯
   - `database/` - 數據庫相關

3. **配置管理**: 使用環境變量或配置文件管理設置

4. **測試**: 使用 pytest 和 httpx 進行測試

## 下一步

- [x] 添加用戶管理 CRUD API
- [ ] 添加數據庫支持（SQLAlchemy + PostgreSQL/MySQL）
- [ ] 實現用戶認證和授權（JWT）
- [ ] 添加日誌記錄
- [ ] 實現緩存（Redis）
- [ ] 添加單元測試
- [ ] 容器化（Docker）
