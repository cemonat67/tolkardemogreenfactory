import os

class Settings:
    API_VERSION = os.getenv("API_VERSION", "v1")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/tolkar")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "60"))
    PLC_HOST = os.getenv("PLC_HOST", "192.168.1.100")
    PLC_PORT = int(os.getenv("PLC_PORT", "502"))
    SCADA_API_URL = os.getenv("SCADA_API_URL", "http://scada.factory.local/api")
    SMARTEX_API_KEY = os.getenv("SMARTEX_API_KEY", "")
    SMARTEX_BASE_URL = os.getenv("SMARTEX_BASE_URL", "https://api.smartex.ai/v1")
    DEMO_MODE = os.getenv("DEMO_MODE", "True").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

settings = Settings()
