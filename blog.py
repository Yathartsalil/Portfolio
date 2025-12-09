from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Optional

app = FastAPI(title="YK Blog API")

# CORS (allow from frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for dev; consider locking this down for prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Database ----------
conn = sqlite3.connect("blog.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    comment TEXT NOT NULL,
    FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS likes (
    post_id INTEGER PRIMARY KEY,
    likes INTEGER DEFAULT 0,
    FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE
)
""")

conn.commit()

# ---------- Models ----------
class PostIn(BaseModel):
    title: str
    body: str

class CommentIn(BaseModel):
    post_id: int
    comment: str

class PostOut(BaseModel):
    id: int
    title: str
    body: str
    date: Optional[str]

# ---------- Helpers ----------
ADMIN_KEY = "supersecretadminkey123"  # keep same key used in frontend

def row_to_post(r):
    return {"id": r[0], "title": r[1], "body": r[2], "date": r[3]}

# ---------- Routes ----------
@app.get("/posts", response_model=List[PostOut])
def get_posts():
    cursor.execute("SELECT id, title, body, date FROM posts ORDER BY id DESC")
    rows = cursor.fetchall()
    return [row_to_post(r) for r in rows]

@app.post("/add-post")
def add_post(data: PostIn, admin_key: str = Query(...)):
    if admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    date = datetime.now().strftime("%d %b %Y")
    cursor.execute("INSERT INTO posts (title, body, date) VALUES (?, ?, ?)", (data.title, data.body, date))
    conn.commit()
    return {"success": True, "message": "Post added"}

@app.delete("/delete-post/{post_id}")
def delete_post(post_id: int, admin_key: str = Query(...)):
    if admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    cursor.execute("DELETE FROM posts WHERE id=?", (post_id,))
    cursor.execute("DELETE FROM comments WHERE post_id=?", (post_id,))
    cursor.execute("DELETE FROM likes WHERE post_id=?", (post_id,))
    conn.commit()
    return {"success": True, "message": "Post deleted"}

@app.get("/comments/{post_id}", response_model=List[str])
def get_comments(post_id: int):
    cursor.execute("SELECT comment FROM comments WHERE post_id=? ORDER BY id ASC", (post_id,))
    return [c[0] for c in cursor.fetchall()]

@app.post("/add-comment")
def add_comment(data: CommentIn):
    # ensure post exists
    cursor.execute("SELECT 1 FROM posts WHERE id=?", (data.post_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Post not found")
    cursor.execute("INSERT INTO comments (post_id, comment) VALUES (?, ?)", (data.post_id, data.comment))
    conn.commit()
    return {"success": True, "message": "Comment added"}

@app.post("/like/{post_id}")
def like_post(post_id: int):
    # ensure post exists
    cursor.execute("SELECT 1 FROM posts WHERE id=?", (post_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Post not found")
    cursor.execute("INSERT OR IGNORE INTO likes (post_id, likes) VALUES (?,0)", (post_id,))
    cursor.execute("UPDATE likes SET likes = likes + 1 WHERE post_id=?", (post_id,))
    conn.commit()
    return {"success": True, "message": "Liked"}

@app.get("/likes/{post_id}")
def get_likes(post_id: int):
    cursor.execute("SELECT likes FROM likes WHERE post_id=?", (post_id,))
    r = cursor.fetchone()
    return {"likes": r[0] if r else 0}


# Optional: seed initial posts if none exist (so static posts can match by title)
def seed_initial_posts():
    cursor.execute("SELECT COUNT(*) FROM posts")
    count = cursor.fetchone()[0]
    if count == 0:
        sample = [
            ("Building My Mars Rover", "Today I improved the soil analysis algorithm, added ultrasonic stabilization and configured the Telemetry V3 dashboard..."),
            ("Why I Love Embedded Systems", "Microcontrollers give you real-world control. I explain why Arduino + C++ + sensors are still unbeatable...")
        ]
        for title, body in sample:
            cursor.execute("INSERT INTO posts (title, body, date) VALUES (?, ?, ?)", (title, body, datetime.now().strftime("%d %b %Y")))
        conn.commit()

# seed on startup
seed_initial_posts()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("blog:app", host="127.0.0.1", port=8000, reload=True)
