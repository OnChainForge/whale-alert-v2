from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime

from app.database import Base


class WhaleAlert(Base):
    """A detected whale-sized Ethereum transaction."""
    __tablename__ = "whale_alerts"

    id = Column(Integer, primary_key=True, index=True)
    tx_hash = Column(String(80), unique=True, nullable=False, index=True)
    block_number = Column(Integer, nullable=False, index=True)
    from_address = Column(String(80), nullable=False)
    to_address = Column(String(80), nullable=True)
    value_eth = Column(Float, nullable=False)
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
