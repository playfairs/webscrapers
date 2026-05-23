from extract import get_twitter_client, fetch_tweets
from scrape import download_images
from write_db import save_to_csv
from config import USERNAME

def main():
    client = get_twitter_client()

    user = client.get_user(username=USERNAME)
    user_id = user.data.id
    print(f"fetching tweets for user: {USERNAME} (ID: {user_id})")

    tweets, media_list = fetch_tweets(client, user_id)
    print(f"fetched {len(tweets)} tweets from {USERNAME}")

    download_images(tweets, media_list)

    save_to_csv(tweets, media_list)
    print("ok")

if __name__ == "__main__":
    main()
