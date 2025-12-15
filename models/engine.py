import logging
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)

from configs import config
if config.DB_ENABLED:
    engine = create_engine(
        config.DATABASE_URI,
        pool_size=config.POOL_SIZE,
        max_overflow=20,  # 允许超过 pool_size 的额外连接数
        pool_recycle=3600,  # 1小时后回收连接，避免使用过期连接
        pool_pre_ping=True,  # 每次从池中获取连接前先测试连接是否有效
        pool_timeout=30,  # 从池中获取连接的超时时间（秒）
        echo_pool=False,  # 生产环境关闭连接池日志
        connect_args={
            "connect_timeout": 10,  # 数据库连接超时（秒）
        }
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Dependency
    def get_session()-> Optional[Session]:
        session  = SessionLocal()
        return session

    @contextmanager
    def get_db() -> Generator[Session, None, None]:
        with get_session() as session:
            try:
                yield session
            finally:
                session.close()
else:
    logger.info("Database is not enabled, skipping database setup.")
    engine = None
    SessionLocal = None

    # Dependency
    def get_session()-> Optional[Session]:
        return None

    @contextmanager
    def get_db() -> Generator[Optional[Session], None, None]:
        yield None