import os
import sqlite3
import time

DB_PATH = os.getenv("DB_PATH", "vault.db")


class VaultDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._init_schema()

    def _init_schema(self):
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                wallet_address TEXT PRIMARY KEY,
                deposit_usdc REAL NOT NULL,
                deposit_ts INTEGER NOT NULL,
                active INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_address TEXT,
                event_type TEXT,
                note TEXT,
                ts INTEGER
            );
            CREATE TABLE IF NOT EXISTS funding_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rate REAL,
                ts INTEGER
            );
            """
        )
        self.conn.commit()

    def register_deposit(self, wallet: str, amount_usdc: float):
        self.conn.execute(
            "INSERT OR REPLACE INTO users VALUES (?, ?, ?, 1)",
            (wallet, amount_usdc, int(time.time())),
        )
        self.conn.commit()

    def get_active_users(self) -> list:
        cur = self.conn.execute(
            "SELECT wallet_address, deposit_usdc FROM users WHERE active=1"
        )
        return [{"wallet_address": r[0], "deposit_usdc": r[1]} for r in cur.fetchall()]

    def get_user(self, wallet: str) -> dict | None:
        cur = self.conn.execute(
            "SELECT wallet_address, deposit_usdc, active FROM users WHERE wallet_address=?",
            (wallet,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "wallet_address": row[0],
            "deposit_usdc": row[1],
            "active": bool(row[2]),
        }

    def deactivate_user(self, wallet: str):
        self.conn.execute("UPDATE users SET active=0 WHERE wallet_address=?", (wallet,))
        self.conn.commit()

    def record_event(self, wallet: str, event_type: str, note: str = ""):
        self.conn.execute(
            "INSERT INTO events VALUES (NULL,?,?,?,?)",
            (wallet, event_type, note, int(time.time())),
        )
        self.conn.commit()

    def record_funding_rate(self, rate: float):
        self.conn.execute(
            "INSERT INTO funding_history VALUES (NULL,?,?)", (rate, int(time.time()))
        )
        self.conn.commit()

    def get_funding_history(self, limit: int = 100) -> list:
        cur = self.conn.execute(
            "SELECT rate, ts FROM funding_history ORDER BY ts DESC LIMIT ?", (limit,)
        )
        return [{"rate": r[0], "ts": r[1]} for r in cur.fetchall()]
