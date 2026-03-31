import json
import time
import uuid

import base58
from solders.keypair import Keypair


def sort_json_keys(value):
    """Recursively sort JSON keys for deterministic Pacifica signatures."""
    if isinstance(value, dict):
        return {k: sort_json_keys(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return [sort_json_keys(item) for item in value]
    return value


def build_and_sign(keypair: Keypair, operation_type: str, operation_data: dict) -> dict:
    """Build and sign a Pacifica payload using compact sorted JSON."""
    timestamp = int(time.time() * 1_000)
    expiry_window = 30_000

    data_to_sign = {
        "timestamp": timestamp,
        "expiry_window": expiry_window,
        "type": operation_type,
        "data": operation_data,
    }

    sorted_message = sort_json_keys(data_to_sign)
    compact_json = json.dumps(sorted_message, separators=(",", ":"))
    signature = keypair.sign_message(compact_json.encode("utf-8"))
    signature_b58 = base58.b58encode(bytes(signature)).decode("ascii")

    return {
        "account": str(keypair.pubkey()),
        "agent_wallet": None,
        "signature": signature_b58,
        "timestamp": timestamp,
        "expiry_window": expiry_window,
        **operation_data,
    }


def build_approval_payload(
    user_keypair: Keypair,
    builder_code: str,
    max_fee_rate: str = "0.001",
) -> dict:
    operation_data = {
        "builder_code": builder_code,
        "max_fee_rate": max_fee_rate,
    }
    return build_and_sign(user_keypair, "approve_builder_code", operation_data)


def build_revoke_payload(user_keypair: Keypair, builder_code: str) -> dict:
    operation_data = {"builder_code": builder_code}
    return build_and_sign(user_keypair, "revoke_builder_code", operation_data)


def build_market_order_payload(
    vault_keypair: Keypair,
    user_account: str,
    symbol: str,
    side: str,
    amount: str,
    builder_code: str,
    slippage_percent: str = "0.5",
    reduce_only: bool = False,
) -> dict:
    operation_data = {
        "symbol": symbol,
        "amount": amount,
        "side": side,
        "slippage_percent": slippage_percent,
        "reduce_only": reduce_only,
        "client_order_id": str(uuid.uuid4()),
        "builder_code": builder_code,
    }
    payload = build_and_sign(vault_keypair, "create_market_order", operation_data)
    payload["account"] = user_account
    return payload
