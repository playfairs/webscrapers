import sqlite3
import os
import argparse

parser = argparse.ArgumentParser
parser.add_argument("db")
args = parser.parse_args()

DB = args.db
OUT = "images"

os.makedirs(OUT, exist_ok=True)

def ext(b):
    if b.startswith(b"\x89PNG"):
        return "png"
    if b.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if b.startswith(b"RIFF") and b[8:12] == b"WEBP":
        return "webp"
    return "bin"

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("SELECT id, image FROM posts WHERE image IS NOT NULL")

for post_id, blob in cur.fetchall():
    e = ext(blob)
    with open(f"{OUT}/post_{post_id}.{e}", "wb") as f:
        f.write(blob)

conn.close()
print("Image extraction complete, u fucking gooner")

