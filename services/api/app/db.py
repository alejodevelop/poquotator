import os
import json
import logging
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.pool import SimpleConnectionPool

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://poquotator:poquotator@db:5432/poquotator")
_pool: Optional[SimpleConnectionPool] = None

def init_pool(minconn: int = 1, maxconn: int = 5):
    global _pool
    if _pool is None:
        _pool = SimpleConnectionPool(minconn, maxconn, DATABASE_URL)
        logger.info("DB pool initialized")

def get_pool() -> SimpleConnectionPool:
    global _pool
    if _pool is None:
        init_pool()
    assert _pool is not None
    return _pool

def close_pool():
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None
        logger.info("DB pool closed")

def log_event(
    *,
    from_email: str,
    subject: str,
    items: List[Dict[str, Any]],
    availability: Dict[str, bool],
    pricing: Dict[str, float],
    currency: str,
    status: str,
    missing: Optional[List[str]],
    quote_id: Optional[str],
    latency_ms: Optional[int],
):
    pool = get_pool()
    conn = pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO events(
                    from_email, subject, items_json, availability_json,
                    pricing_json, currency, status, missing_json, quote_id, latency_ms
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    from_email,
                    subject,
                    json.dumps(items),
                    json.dumps(availability),
                    json.dumps(pricing),
                    currency,
                    status,
                    json.dumps(missing) if missing is not None else None,
                    quote_id,
                    latency_ms,
                ),
            )
    finally:
        pool.putconn(conn)
