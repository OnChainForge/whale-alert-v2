from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    log_level: str = "INFO"
    ethereum_rpc_url: str
    poll_interval_seconds: int = 15
    whale_threshold_eth: float = 50.0
    redis_url: str = "redis://localhost:6379/0"
    redis_dedup_ttl_seconds: int = 86400

    class Config:
        env_file = ".env"


settings = Settings()
