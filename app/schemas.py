from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class WhaleAlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tx_hash: str
    block_number: int
    from_address: str
    to_address: Optional[str]
    value_eth: float
    detected_at: datetime
