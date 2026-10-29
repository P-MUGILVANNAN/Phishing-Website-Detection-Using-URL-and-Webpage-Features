from pathlib import Path
import os

class Settings:
    def __init__(self):
        self.BASE_DIR: Path = Path(__file__).resolve().parent.parent
        self.ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
        self.PROJECT_NAME: str = os.getenv("PROJECT_NAME", "PhishGuard AI")
        self.VERSION: str = os.getenv("VERSION", "1.0.0")
        self.API_PREFIX: str = os.getenv("API_PREFIX", "/api")
        
        # Database & Artifacts
        db_path = os.getenv("DATABASE_URL", "sqlite:///./phishguard.db")
        if db_path.startswith("sqlite:///./"):
            self.DATABASE_PATH: Path = self.BASE_DIR / db_path.replace("sqlite:///./", "")
            self.DATABASE_URL: str = f"sqlite:///{self.DATABASE_PATH}"
        else:
            self.DATABASE_URL = db_path
            self.DATABASE_PATH = self.BASE_DIR / "phishguard.db"
            
        artifacts_env = os.getenv("ARTIFACTS_DIR", "./artifacts")
        if artifacts_env.startswith("./") or not Path(artifacts_env).is_absolute():
            self.ARTIFACTS_DIR: Path = self.BASE_DIR / artifacts_env.lstrip("./")
        else:
            self.ARTIFACTS_DIR: Path = Path(artifacts_env)
            
        self.ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Safe URL Fetching controls
        self.ENABLE_WEBPAGE_FETCH: bool = os.getenv("ENABLE_WEBPAGE_FETCH", "false").lower() in ("true", "1", "yes")
        self.SAFE_FETCH_TIMEOUT_SECONDS: float = float(os.getenv("SAFE_FETCH_TIMEOUT_SECONDS", "6.0"))
        self.SAFE_FETCH_MAX_BYTES: int = int(os.getenv("SAFE_FETCH_MAX_BYTES", "524288"))  # 512 KB
        self.SAFE_FETCH_MAX_REDIRECTS: int = int(os.getenv("SAFE_FETCH_MAX_REDIRECTS", "3"))
        
        # Classification thresholds
        self.THRESHOLD_LEGITIMATE: float = float(os.getenv("THRESHOLD_LEGITIMATE", "0.30"))
        self.THRESHOLD_PHISHING: float = float(os.getenv("THRESHOLD_PHISHING", "0.70"))
        
        # Security & Feature Versioning
        self.ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "dev-secret-key")
        self.FEATURE_SCHEMA_VERSION: str = os.getenv("FEATURE_SCHEMA_VERSION", "1.0.0")
        
        # Allowed schemes
        self.ALLOWED_SCHEMES = {"http", "https"}

settings = Settings()

