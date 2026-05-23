import aiosqlite
import httpx
import asyncio

class DB:
    def __init__(self, db_name):
        self.db_path = db_name
        self.duplicates = 0

    async def fetch_images(self, images):
        try:
            async with httpx.AsyncClient() as client:
                tasks = [client.get(image) for image in images]
                responses = await asyncio.gather(*tasks)
                return [response.content for response in responses if response.status_code == 200]
        except Exception as e:
            print(f"Error fetching images: {e}")
            return []
        
    async def write(self, perma, images, nsfw):
        async with aiosqlite.connect(self.db_path) as db:
            images = await self.fetch_images(images)
            for img in images:
                cursor = await db.cursor()
                req = await cursor.execute('SELECT id FROM posts WHERE permalink = ? AND image = ?', (perma, img))
                check = await req.fetchall()
                if check:
                    self.duplicates += 1
                    continue
                await db.execute('''
                    INSERT INTO posts (permalink, image, nsfw)
                    VALUES (?, ?, ?)
                    ''', (perma, img, nsfw))
            await db.commit()

    async def create_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    permalink TEXT,
                    image BLOB,
                    nsfw BOOL
                )
                ''')
            await db.commit()

    async def read(self, perma = None, id = None):
        if not perma and not id:
            raise ValueError("Either permalink or id must be provided")
        async with aiosqlite.connect(self.db_path) as db:
            if perma:
                async with db.execute('SELECT image FROM posts WHERE permalink = ?', (perma,)) as cursor:
                    rows = await cursor.fetchall()
                    return [row[0] for row in rows]
            if id:
                async with db.execute('SELECT image FROM posts WHERE id = ?', (id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return [row[0]]
    
    async def count(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT COUNT(*) FROM posts') as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
