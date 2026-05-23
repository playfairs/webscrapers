import os
import requests
from config import DOWNLOAD_FOLDER

def download_images(tweets, media_list):
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    media_dict = {m["media_key"]: m for m in media_list}

    image_count = 0
    for tweet in tweets:
        if hasattr(tweet, "attachments") and "media_keys" in tweet.attachments:
            for key in tweet.attachments["media_keys"]:
                media = media_dict.get(key)
                if media and media["type"] == "photo":
                    url = media["url"]
                    try:
                        img_data = requests.get(url).content
                        img_name = os.path.join(DOWNLOAD_FOLDER, url.split("/")[-1])
                        with open(img_name, "wb") as f:
                            f.write(img_data)
                        image_count += 1
                        print(f"[{image_count}] Downloaded: {img_name}")
                    except Exception as e:
                        print(f"Failed to download {url}: {e}")

    print(f"finished downloading {image_count} images.")
