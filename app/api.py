from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api_analytics.fastapi import Analytics
from routes import user, prediction, balance, history
from database.database import init_db
from services.crud.mlservice import MLService
import uvicorn
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ML Service API", version="1.0.0")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Адрес вашего Streamlit приложения
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# https://pypi.org/project/fastapi-analytics/
app.add_middleware(Analytics, api_key="3e9521c9-6c4b-4ed2-b8e6-d48d2fbbcbf1")  # Add middleware

ml_service = MLService()

@app.on_event("startup")
async def on_startup():
    try:
        init_db()
        logger.info("Database initialized successfully")
        # Инициализация MLService перенесена сюда
        global ml_service
        ml_service = MLService()
        logger.info("ML Service initialized successfully")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(prediction.router, prefix="/prediction", tags=["prediction"])
app.include_router(balance.router, prefix="/balance", tags=["balance"])
app.include_router(history.router, prefix="/history", tags=["history"])

@app.get("/", tags=["root"])
async def root():
    return {"message": "Welcome to the ML Service API", "version": app.version}

if __name__ == "__main__":
    uvicorn.run('api:app', host='0.0.0.0', port=8080, reload=True)