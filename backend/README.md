# Smart Office Backend

## Setup

```bash
pip install -r requirements.txt
```

## Run

### Development
```bash
fastapi dev backend/app/main.py
```

### Final
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
