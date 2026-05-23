import asyncio
import colorama
import httpx
import time as t
from base64 import b64encode
from datetime import datetime
from reddit import parse_reddit_posts
from typing import List, Union
from urllib.parse import quote_plus
from write_db import DB

class Scraper:
    def __init__(self, subreddit: str):
        self.subreddit = subreddit
        self.headers = {
            'accept': 'text/vnd.reddit.partial+html, text/html;q=0.9',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'priority': 'u=1, i',
            'referer': f'https://www.reddit.com/r/{subreddit}/',
            'sec-ch-ua': '"Brave";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        }

    async def get_init_post(self, subreddit: str, mode: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'https://www.reddit.com/r/{subreddit}/{mode}/?t=ALL',
                headers=self.headers,
                timeout=5
            )
        if response.status_code != 200:
            raise Exception(f"Failed to fetch initial post: {response.status_code}")
        return parse_reddit_posts(response.text)

    async def get_reddit_posts(self, after: str, mode: str):
        params = {
            't': 'ALL',
            'after': after,
            'name': self.subreddit,
            'feedLength': '45',
            'distance': '55',
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'https://www.reddit.com/svc/shreddit/community-more-posts/{mode}/',
                params=params,
                headers=self.headers,
                timeout=5
            )
        if response.status_code != 200:
            raise Exception(f"Failed to fetch posts: {response.status_code}")
        return response.text

    async def scrape_reddit_posts(self, after: str, mode: str):
        html = await self.get_reddit_posts(after, mode)
        return parse_reddit_posts(html)

    def t3toid(self, t3):
        if not t3.startswith("t3_"):
            t3 = f"t3_{t3}"
        return quote_plus(b64encode(t3.encode('utf-8')).decode('utf-8'))

async def main(sub, dbname="db", posts=1500, json=False, mode: Union[str, List[str]]=None, allow_all_media=False):
    start = t.time()
    db = DB(f'{dbname}.db')
    await db.create_db()
    fetched = []
    subreddit = sub
    sc = Scraper(subreddit)
    queue = asyncio.Queue()
    modes = ["top", "best", "hot", "new", "rising"] if not mode else list(mode)

    async def db_writer():
        while True:
            item = await queue.get()
            if item is None:
                break
            permalink, media_urls, nsfw = item
            await db.write(permalink, media_urls, nsfw)
            queue.task_done()

    writer_task = asyncio.create_task(db_writer())
    print(f"{colorama.Fore.YELLOW}Scraping r/{subreddit} for {posts} posts...{colorama.Style.RESET_ALL}")
    for mode in modes:
        print(f"{colorama.Fore.CYAN}Scraping mode: {mode}{colorama.Style.RESET_ALL}")
        init = await sc.get_init_post(subreddit, mode)
        if not init:
            print(f"{colorama.Fore.YELLOW}No initial posts found for mode '{mode}'. Skipping...{colorama.Style.RESET_ALL}")
            continue
        fetched += init
        after = init[-1]["id"]
        allowed_types = ["image", "gallery"]
        if allow_all_media:
            allowed_types.append("video")
            allowed_types.append("gif")
        for i in range(1, (posts // 25)+1):
            time_str = datetime.now().strftime("[%H:%M:%S]")
            try:
                posts_batch = await sc.scrape_reddit_posts(after, mode)
            except Exception as e:
                print(f"{colorama.Fore.YELLOW}{time_str} - {colorama.Fore.RED} Failed to fetch posts: {e}, skipping... - {colorama.Fore.MAGENTA}Attempt #{i}{colorama.Style.RESET_ALL}")
                continue
            fetched += posts_batch
            if posts_batch:
                id = posts_batch[-1]["id"]
                for post in posts_batch:
                    if not post.get("post_type") in allowed_types:
                        continue
                    await queue.put((post["permalink"], post.get("media_urls", []), post.get("nsfw", False)))
                after = id
            else:
                print(f"{colorama.Fore.YELLOW}{time_str} - {colorama.Fore.RED} No more posts found, stopping... - {colorama.Fore.MAGENTA}Attempt #{i}{colorama.Style.RESET_ALL}")
                break
            print(f"{colorama.Fore.YELLOW}{time_str} - {colorama.Fore.GREEN}Scraped {len(posts_batch)} posts (Total: {len(fetched)}) - {colorama.Fore.MAGENTA}Attempt #{i}{colorama.Style.RESET_ALL}")
            await asyncio.sleep(0.5)
            
    print(f"{colorama.Fore.YELLOW}Finished scraping {len(fetched)-3} posts from r/{subreddit} - {colorama.Fore.MAGENTA}Total time taken: {round(t.time() - start, 2)} seconds. {colorama.Fore.CYAN}Writing to database... {colorama.Style.RESET_ALL}")
    if json:
        import json
        with open(f"{subreddit}.json", "w", encoding="utf-8") as f:
            json.dump(fetched, f, indent=4, ensure_ascii=False)
    await queue.join()
    await queue.put(None)
    await writer_task
    print(f"{colorama.Fore.GREEN}Database write complete! {colorama.Fore.RED} Total duplicates: {db.duplicates}. Time taken: {round(t.time() - start, 2)} seconds{colorama.Style.RESET_ALL}")
    
if __name__ == "__main__":
    subreddits_input = input("put the subreddit(s) u want to scrape (comma separated): ").strip()
    subreddits = [sub.strip() for sub in subreddits_input.split(",")]
    
    db_name = input("Enter database name (without .db extension otherwise you'll jus have 'name.db.db'): ").strip()
    if not db_name:
        db_name = "db"
    
    for sub in subreddits:
        asyncio.run(main(sub, db_name, 5000, True))
    
    print(f"{colorama.Fore.GREEN}Done, Database '{db_name}.db' is ready for extraction.{colorama.Style.RESET_ALL}")