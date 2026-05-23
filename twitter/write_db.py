import pandas as pd

def save_to_csv(tweets, media_list, filename="tweets_media.csv"):
    media_dict = {m["media_key"]: m for m in media_list}
    data = []

    for tweet in tweets:
        if hasattr(tweet, "attachments") and "media_keys" in tweet.attachments:
            for key in tweet.attachments["media_keys"]:
                media = media_dict.get(key)
                if media and media["type"] == "photo":
                    data.append({
                        "tweet_id": tweet.id,
                        "text": tweet.text,
                        "media_url": media["url"]
                    })

    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"saved metadata to {filename}")
