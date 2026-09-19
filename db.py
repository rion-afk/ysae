import sqlite3, time, config

SCHEMA = """
CREATE TABLE IF NOT EXISTS experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL, video_id TEXT,
    hook_template TEXT, seed INTEGER, prompt_version TEXT,
    cut_rhythm TEXT, music_track TEXT, title_variant TEXT,
    retention_3s REAL, retention_avg REAL, replay_ratio REAL,
    views INTEGER DEFAULT 0, status TEXT DEFAULT 'draft'
);
CREATE TABLE IF NOT EXISTS bandit (
    arm TEXT PRIMARY KEY, alpha REAL DEFAULT 1, beta REAL DEFAULT 1
);
"""

class DB:
    def __init__(self, path=config.DB_PATH):
        # Timeout lungo e check_same_thread evitano "database is locked" nei loop lunghi
        self.c = sqlite3.connect(path, timeout=15, check_same_thread=False)
        self.c.executescript(SCHEMA)

    def log_experiment(self, **kw):
        kw.setdefault("ts", time.time())
        cols = ",".join(kw)
        self.c.execute(f"INSERT INTO experiments ({cols}) VALUES ({','.join('?'*len(kw))})",
                       list(kw.values()))
        self.c.commit()

    def update_result(self, video_id, **kw):
        sets = ",".join(f"{k}=?" for k in kw)
        self.c.execute(f"UPDATE experiments SET {sets} WHERE video_id=?", [*kw.values(), video_id])
        self.c.commit()

    def all(self, where="1=1", args=()):
        self.c.row_factory = sqlite3.Row
        return self.c.execute(f"SELECT * FROM experiments WHERE {where}", args).fetchall()

    def bandit_update(self, arm, success: bool):
        self.c.execute("INSERT OR IGNORE INTO bandit(arm) VALUES(?)", (arm,))
        col = "alpha" if success else "beta"
        self.c.execute(f"UPDATE bandit SET {col}={col}+1 WHERE arm=?", (arm,))
        self.c.commit()

    def bandit_pull(self, arms):
        import random
        rows = {r["arm"]: (r["alpha"], r["beta"]) for r in
                self.c.execute("SELECT * FROM bandit").fetchall()}
        best, best_s = None, -1
        for a in arms:
            al, be = rows.get(a, (1, 1))
            s = random.betavariate(al, be)
            if s > best_s:
                best, best_s = a, s
        return best

db = DB()
