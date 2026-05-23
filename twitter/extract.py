import tweepy
from config import BEARER_TOKEN

def get_twitter_client():
    return tweepy.Client(bearer_token=BEARER_TOKEN)

def fetch_tweets(client, user_id, max_results=100):
    next_token = None
    all_tweets = []
    all_media = []

    while True:
        tweets = client.get_users_tweets(
            id=user_id,
            max_results=max_results,
            expansions=["attachments.media_keys"],
            media_fields=["url", "type"],
            pagination_token=next_token
        )

        if not tweets.data:
            break

        all_tweets.extend(tweets.data)

        if tweets.includes and "media" in tweets.includes:
            all_media.extend(tweets.includes["media"])

        next_token = getattr(tweets.meta, "next_token", None)
        if not next_token:
            break

    return all_tweets, all_media
