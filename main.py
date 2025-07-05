from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os # for environment variables
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse
import logging # for logging
import pymongo.errors
from api.routers.auth import router as auth_router
from api.routers.tasks import router as tasks_router
from api.dependencies.database import get_db
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

# MongoDB settings
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# FastAPI app settings
APP_NAME = os.getenv("APP_NAME")
CLIENT_ORIGIN_URL = os.getenv("CLIENT_ORIGIN_URL", "http://localhost:3000")

# Validate environment variables
if not MONGODB_URI or not DATABASE_NAME:
    raise ValueError("MONGODB_URI and DATABASE_NAME must be set in .env")

# MongoDB client (global, initialized at startup)
client = None
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    global client, db
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    try:
        # Test connection
        await client.server_info()
        logger.info("Connected to MongoDB")
        yield
    except pymongo.errors.ConnectionError as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
    finally:
        # Shutdown: Close MongoDB connection
        client.close()
        logger.info("Disconnected from MongoDB")

# Create FastAPI app
app = FastAPI(
    title="TodoApp API",
    description="A comprehensive API for managing tasks, users, and password reset",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc", 
    lifespan=lifespan
)

# CORS middleware
# The CLIENT_ORIGIN_URL should be the URL of your frontend application
origins = [
    CLIENT_ORIGIN_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(auth_router)
app.include_router(tasks_router)

@app.get("/", response_class=HTMLResponse, tags=["Home"])
async def get_root():
    """Welcome page for the TodoApp API."""
    content = """
        <html>
            <head>
                <title>Welcome to TodoApp API</title>
                <style>
                    body { font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333; padding: 20px; }
                    h1 { color: #2c3e50; }
                    a { color: #2980b9; text-decoration: none; }
                    a:hover { text-decoration: underline; }
                    p { font-size: 1.2em; }
                </style>
            </head>
            <body>
                <h1>Welcome to TodoApp API</h1>
                <p>This is a comprehensive API for managing a todo app.</p>
                <p>Visit <a href="/docs">API documentation</a> for details.</p>
            </body>
        </html>
        """
    return HTMLResponse(content=content)


