import asyncio
import logging
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.blockchain import get_latest_block_number, fetch_whale_transactions
from app.models import WhaleAlert
from app.dedup import is_duplicate

logger = logging.getLogger("listener")


def get_last_processed_block(db: Session) -> int | None:
    last = db.query(WhaleAlert).order_by(WhaleAlert.block_number.desc()).first()
    return last.block_number if last else None


def process_block(block_number: int) -> None:
    """
    Fetches a block, finds whale-sized transactions, and stores any
    that haven't been seen before (checked via Redis). Runs in a
    worker thread since it performs blocking RPC calls.
    """
    db = SessionLocal()
    try:
        whales = fetch_whale_transactions(block_number)

        for whale in whales:
            if is_duplicate(whale["tx_hash"]):
                logger.info(f"Skipping duplicate whale tx {whale['tx_hash']}")
                continue

            db_alert = WhaleAlert(**whale)
            db.add(db_alert)
            db.commit()
            logger.info(
                f"WHALE DETECTED: {whale['value_eth']} ETH "
                f"({whale['from_address']} -> {whale['to_address']})"
            )

    except Exception as e:
        logger.error(f"Error processing block {block_number}: {e}")
        db.rollback()
    finally:
        db.close()


async def run_listener_loop():
    """Polls the network for new blocks and checks each for whale transactions."""
    logger.info("Starting whale alert listener...")

    while True:
        try:
            db = SessionLocal()
            try:
                last_processed = get_last_processed_block(db)
            finally:
                db.close()

            latest = get_latest_block_number()
            start_block = latest if last_processed is None else last_processed + 1

            for block_number in range(start_block, latest + 1):
                await asyncio.to_thread(process_block, block_number)

        except Exception as e:
            logger.error(f"Error in listener loop: {e}")

        await asyncio.sleep(settings.poll_interval_seconds)
