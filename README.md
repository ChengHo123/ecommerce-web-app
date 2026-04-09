# 電商網頁應用程式

前後端分離的台灣電商平台。

## 技術棧

| 層級 | 技術 |
|------|------|
| 顧客前台 | Vue 3 + TypeScript + Vite + TailwindCSS |
| 管理後台 | Vue 3 + TypeScript + Vite + TailwindCSS |
| 後端 API | Python + FastAPI + SQLAlchemy |
| 資料庫 | PostgreSQL |
| 快取 | Redis |
| 認證 | LINE Login + JWT |
| 金流 | LINE Pay + Stripe (Apple Pay) |
| 物流 | 綠界 ECPay |

## 快速啟動

### 1. 環境設定

```bash
cp backend/.env.example backend/.env
# 填入 LINE Login、LINE Pay、Stripe、ECPay 金鑰
```

### 2. 啟動服務

```bash
docker-compose up -d postgres redis
```

### 3. 後端

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate       # Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### 4. 前台

```bash
cd frontend
npm install
npm run dev
# http://localhost:5173
```

### 5. 後台管理

```bash
cd admin
npm install
npm run dev
# http://localhost:5174
```

## API 文件

後端啟動後：http://localhost:8000/docs

## 目錄結構

```
ecommerce-web-app/
├── frontend/   # 顧客前台 Vue 3
├── admin/      # 管理後台 Vue 3
├── backend/    # FastAPI 後端
└── docker-compose.yml
```

## 第三方服務設定

| 服務 | 說明 |
|------|------|
| LINE Login | [LINE Developers Console](https://developers.line.biz/) 建立 Login Channel |
| LINE Pay | 申請商戶帳號，取得 Channel ID/Secret |
| Stripe | 建立帳號，設定 Apple Pay 網域驗證 |
| ECPay (綠界) | 申請特店帳號，取得商店代號/HashKey/HashIV |
