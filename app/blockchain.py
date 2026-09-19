import logging
from datetime import datetime, timezone
from web3 import Web3

from app.config import settings

logger = logging.getLogger("blockchain")

w3 = Web3(Web3.HTTPProvider(settings.ethereum_rpc_url))


def get_latest_block_number() -> int:
    """Returns the most recent block number on the network."""
    return w3.eth.block_number


def fetch_whale_transactions(block_number: int) -> list[dict]:
    """
    Fetches a block and returns only the transactions whose value
    meets or exceeds the whale threshold, normalized into flat dicts.
    """
    block = w3.eth.get_block(block_number, full_transactions=True)
    whales = []

    for tx in block["transactions"]:
        value_eth = float(w3.from_wei(tx["value"], "ether"))
        if value_eth < settings.whale_threshold_eth:
            continue

        whales.append({
            "tx_hash": tx["hash"].hex(),
            "block_number": block_number,
            "from_address": tx["from"],
            "to_address": tx["to"],
            "value_eth": value_eth,
        })

    return whales
