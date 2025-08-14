import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class DatabaseType(Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"

@dataclass
class DatabaseConfig:
    database_type: DatabaseType
    host: Optional[str] = None
    port: Optional[int] = None
    database: str = "cnav.db"
    username: Optional[str] = None
    password: Optional[str] = None
    min_pool_size: int = 5
    max_pool_size: int = 10
    pool_timeout: int = 30
    # SQLite specific
    sqlite_path: Optional[str] = None

    @property
    def url(self) -> str:
        """Get async database URL"""
        if self.database_type == DatabaseType.SQLITE:
            db_path = self.sqlite_path or f"./{self.database}"
            return f"sqlite+aiosqlite:///{db_path}"
        elif self.database_type == DatabaseType.POSTGRESQL:
            return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            raise ValueError(f"Unsupported database type: {self.database_type}")

    @property
    def sync_url(self) -> str:
        """Get synchronous database URL"""
        if self.database_type == DatabaseType.SQLITE:
            db_path = self.sqlite_path or f"./{self.database}"
            return f"sqlite:///{db_path}"
        elif self.database_type == DatabaseType.POSTGRESQL:
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            raise ValueError(f"Unsupported database type: {self.database_type}")

    @property
    def is_sqlite(self) -> bool:
        """Check if database is SQLite"""
        return self.database_type == DatabaseType.SQLITE

    @property
    def is_postgresql(self) -> bool:
        """Check if database is PostgreSQL"""
        return self.database_type == DatabaseType.POSTGRESQL

def get_database_config() -> DatabaseConfig:
    """Load database configuration from environment variables."""
    
    # Determine database type from environment
    db_type_str = os.getenv("DB_TYPE", "sqlite").lower()
    try:
        db_type = DatabaseType(db_type_str)
    except ValueError:
        db_type = DatabaseType.SQLITE  # Default to SQLite
    
    # Try to get full DATABASE_URL first
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Parse DATABASE_URL
        if database_url.startswith("postgresql://"):
            url_parts = database_url.replace("postgresql://", "").split("@")
            user_pass = url_parts[0].split(":")
            host_port_db = url_parts[1].split("/")
            host_port = host_port_db[0].split(":")
            
            return DatabaseConfig(
                database_type=DatabaseType.POSTGRESQL,
                host=host_port[0],
                port=int(host_port[1]) if len(host_port) > 1 else 5432,
                database=host_port_db[1],
                username=user_pass[0],
                password=user_pass[1] if len(user_pass) > 1 else "",
            )
        elif database_url.startswith("sqlite://"):
            # Extract SQLite path from URL
            sqlite_path = database_url.replace("sqlite:///", "")
            return DatabaseConfig(
                database_type=DatabaseType.SQLITE,
                database=os.path.basename(sqlite_path),
                sqlite_path=sqlite_path
            )
    
    # Build config based on database type
    if db_type == DatabaseType.SQLITE:
        return DatabaseConfig(
            database_type=DatabaseType.SQLITE,
            database=os.getenv("DB_NAME", "cnav.db"),
            # sqlite_path=os.getenv("DB_PATH", "./cnav.db")
            sqlite_path=os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "cnav.db"))
        )
    else:  # PostgreSQL
        return DatabaseConfig(
            database_type=DatabaseType.POSTGRESQL,
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "cnav_db"),
            username=os.getenv("DB_USER", "cnav_user"),
            password=os.getenv("DB_PASSWORD", ""),
            min_pool_size=int(os.getenv("DB_MIN_POOL_SIZE", "5")),
            max_pool_size=int(os.getenv("DB_MAX_POOL_SIZE", "20")),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
        ) 