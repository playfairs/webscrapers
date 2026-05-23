import httpx
import xml.etree.ElementTree as ET

def get_reddit_posts():
    return httpx.get('https://www.reddit.com/svc/shreddit/community-more-posts/best/?after=dDNfMWt5Nm03dw%3D%3D&t=DAY&name=unixporn&ad_posts_served=1&navigationSessionId=2bd23024-e314-4f92-9cff-b6cfdefd96e7&feedLength=59&distance=55&adDistance=7')

from bs4 import BeautifulSoup
import re

def parse_reddit_posts(html):
    soup = BeautifulSoup(html, "html.parser")
    posts = []

    for post in soup.find_all("shreddit-post"):
        post_data = {}

        title_tag = post.find("a", slot="title")
        post_data["title"] = title_tag.get_text(strip=True) if title_tag else None

        post_data["permalink"] = post.get("permalink")

        post_data["author"] = post.get("author")
        post_data["author_url"] = None
        author_link = post.find("a", href=re.compile(r"^/user/"))
        if author_link:
            post_data["author_url"] = author_link["href"]
        post_data["id"] = post.get('id')
        post_data["score"] = post.get("score")

        post_data["post_type"] = post.get("post-type")

        post_data["created_timestamp"] = post.get("created-timestamp")

        post_data["comment_count"] = post.get("comment-count")

        media_urls = []
        preview_links = set()
        i_links = set()

        for img in post.find_all("img"):
            src = img.get("src")
            if src and '/snoovatar/avatars/' not in src:
                if "preview.redd.it" in src:
                    preview_links.add(src)
                elif "i.redd.it" in src:
                    i_links.add(src)
        for gallery in post.find_all("gallery-carousel"):
            for img in gallery.find_all("img"):
                src = img.get("src")
                if src and '/snoovatar/avatars/' not in src:
                    if "preview.redd.it" in src:
                        preview_links.add(src)
                    elif "i.redd.it" in src:
                        i_links.add(src)
        for player in post.find_all("shreddit-player-2"):
            src = player.get("src")
            if src:
                i_links.add(src)
            poster = player.get("poster")
            if poster:
                i_links.add(poster)

        if preview_links:
            media_urls = list(preview_links)
        else:
            media_urls = list(i_links)

        post_data["media_urls"] = media_urls

        post_data["nsfw"] = post.has_attr("nsfw")

        posts.append(post_data)
    return posts
