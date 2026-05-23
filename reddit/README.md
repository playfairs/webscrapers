# Reddit Image Scraper

A tool to scrape images from Reddit subreddits and extract them from a SQLite database.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Scraping Images

Run the scraper to fetch posts and images from subreddits:

```bash
python scrape.py
```

You'll be prompted to enter:
- Subreddit(s) to scrape (comma-separated for multiple)
- Database name (without .db extension)

Example:
```
put the subreddit(s) u want to scrape (comma separated): wallpapers, earthporn
Enter database name (without .db extension otherwise you'll jus have 'name.db.db'): reddit_images
```

### Extracting Images

Extract images from the database to files:

```bash
python extract.py <database_path>
```

Example:
```bash
python extract.py reddit_images.db
```

Images will be saved to the `images/` directory with filenames like `post_123.png`.

## Files

- `scrape.py` - Main scraper that fetches Reddit posts and saves to database
- `extract.py` - Extracts images from the database to files
- `write_db.py` - Database handler class
- `reddit.py` - Reddit HTML parser
