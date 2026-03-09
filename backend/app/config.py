import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_ROOT / ".env")

# Mongo
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# AWS
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET = os.getenv("AWS_BUCKET")
AWS_S3_PREFIX = os.getenv("AWS_S3_PREFIX")

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "")
CORS_ORIGIN_REGEX = os.getenv(
	"CORS_ORIGIN_REGEX",
	r"^https://wafer-map-pattern-system(?:-[a-z0-9-]+)?\.vercel\.app$",
)