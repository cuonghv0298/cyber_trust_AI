import logging
from contextlib import contextmanager, asynccontextmanager
from typing import AsyncGenerator, Generator, Optional, Dict, Any, Union

# Sync imports
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, StaticPool

# Async imports
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .config import DatabaseConfig, get_database_config, DatabaseType
from .models import Base

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager supporting both sync and async operations for PostgreSQL and SQLite"""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or get_database_config()
        
        # Async components
        self._async_engine: Optional[AsyncEngine] = None
        self._async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None
        
        # Sync components
        self._sync_engine = None
        self._sync_session_maker: Optional[sessionmaker[Session]] = None
        
        self._async_initialized = False
        self._sync_initialized = False

    # === Async Methods ===
    
    async def initialize_async(self) -> None:
        """Initialize async database connection"""
        if self._async_initialized:
            return

        try:
            engine_kwargs: Dict[str, Any] = {
                "echo": False,  # Set to True for SQL debugging
            }

            # Configure pooling based on database type
            if self.config.is_sqlite:
                # SQLite specific configuration
                engine_kwargs["poolclass"] = StaticPool
                engine_kwargs["connect_args"] = {
                    "check_same_thread": False,  # Allow multi-threading for SQLite
                }
            else:
                # PostgreSQL specific configuration
                if self.config.host == "localhost":
                    engine_kwargs["poolclass"] = NullPool
                else:
                    engine_kwargs["pool_size"] = self.config.min_pool_size
                    engine_kwargs["max_overflow"] = self.config.max_pool_size - self.config.min_pool_size
                    engine_kwargs["pool_timeout"] = self.config.pool_timeout

            # Create async engine
            self._async_engine = create_async_engine(
                self.config.url,
                **engine_kwargs,
            )

            # Create async session maker
            self._async_session_maker = async_sessionmaker(
                bind=self._async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            # Create tables if they don't exist
            async with self._async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            self._async_initialized = True
            logger.info(f"Async database initialized successfully ({self.config.database_type.value})")
                
        except Exception as e:
            logger.error(f"Failed to initialize async database: {e}", exc_info=True)
            raise

    async def close_async(self) -> None:
        """Close async database connection"""
        if self._async_engine:
            await self._async_engine.dispose()
            self._async_engine = None
            self._async_session_maker = None
            self._async_initialized = False
            logger.info("Async database closed successfully")

    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session"""
        if not self._async_initialized:
            await self.initialize_async()

        if not self._async_session_maker:
            raise RuntimeError("Async database not initialized")

        async with self._async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Async database session error: {e}")
                raise

    # === Sync Methods ===
    
    def initialize_sync(self) -> None:
        """Initialize sync database connection"""
        if self._sync_initialized:
            return

        try:
            engine_kwargs: Dict[str, Any] = {
                "echo": False,  # Set to True for SQL debugging
            }

            # Configure pooling based on database type
            if self.config.is_sqlite:
                # SQLite specific configuration
                engine_kwargs["poolclass"] = StaticPool
                engine_kwargs["connect_args"] = {
                    "check_same_thread": False,  # Allow multi-threading for SQLite
                }
            else:
                # PostgreSQL specific configuration
                if self.config.host == "localhost":
                    engine_kwargs["poolclass"] = NullPool
                else:
                    engine_kwargs["pool_size"] = self.config.min_pool_size
                    engine_kwargs["max_overflow"] = self.config.max_pool_size - self.config.min_pool_size
                    engine_kwargs["pool_timeout"] = self.config.pool_timeout

            # Create sync engine
            self._sync_engine = create_engine(
                self.config.sync_url,
                **engine_kwargs,
            )

            # Create sync session maker
            self._sync_session_maker = sessionmaker(
                bind=self._sync_engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )

            # Create tables if they don't exist
            Base.metadata.create_all(bind=self._sync_engine)

            self._sync_initialized = True
            logger.info(f"Sync database initialized successfully ({self.config.database_type.value})")
                
        except Exception as e:
            logger.error(f"Failed to initialize sync database: {e}", exc_info=True)
            raise

    def close_sync(self) -> None:
        """Close sync database connection"""
        if self._sync_engine:
            self._sync_engine.dispose()
            self._sync_engine = None
            self._sync_session_maker = None
            self._sync_initialized = False
            logger.info("Sync database closed successfully")

    @contextmanager
    def get_sync_session(self) -> Generator[Session, None, None]:
        """Get a sync database session"""
        if not self._sync_initialized:
            self.initialize_sync()

        if not self._sync_session_maker:
            raise RuntimeError("Sync database not initialized")

        session = self._sync_session_maker()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Sync database session error: {e}")
            raise
        finally:
            session.close()

    # === Health Check Methods ===
    
    async def async_health_check(self) -> bool:
        """Check async database connection health"""
        try:
            async with self.get_async_session() as session:
                await session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Async database health check failed: {e}")
            return False

    def sync_health_check(self) -> bool:
        """Check sync database connection health"""
        try:
            with self.get_sync_session() as session:
                session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Sync database health check failed: {e}")
            return False

    # === Properties ===
    
    @property
    def is_async_initialized(self) -> bool:
        """Check if async database is initialized"""
        return self._async_initialized

    @property
    def is_sync_initialized(self) -> bool:
        """Check if sync database is initialized"""
        return self._sync_initialized

    @property
    def database_type(self) -> DatabaseType:
        """Get the database type"""
        return self.config.database_type

# === Global Database Manager ===

_db_manager: Optional[DatabaseManager] = None

def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

# === Convenience Functions ===

async def init_async_database() -> None:
    """Initialize async database connection"""
    db_manager = get_database_manager()
    await db_manager.initialize_async()

def init_sync_database() -> None:
    """Initialize sync database connection"""
    db_manager = get_database_manager()
    db_manager.initialize_sync()

async def close_async_database() -> None:
    """Close async database connection"""
    global _db_manager
    if _db_manager:
        await _db_manager.close_async()
        _db_manager = None

def close_sync_database() -> None:
    """Close sync database connection"""
    global _db_manager
    if _db_manager:
        _db_manager.close_sync()
        _db_manager = None

@contextmanager
def get_sync_session() -> Generator[Session, None, None]:
    """Get a sync database session (context manager)"""
    db_manager = get_database_manager()
    with db_manager.get_sync_session() as session:
        yield session

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session (async context manager)"""
    db_manager = get_database_manager()
    async with db_manager.get_async_session() as session:
        yield session