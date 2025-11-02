# Twitter Search Scraper

A Python tool for scraping tweets from specific Twitter users using the Twitter OpenAPI. This scraper allows you to collect tweets within a specified date range and save them in JSONL format.

## Features

- 🔍 Search and scrape tweets from specific Twitter users
- 📅 Filter tweets by date range (since/until)
- 💾 Export tweets to JSONL format
- ⏱️ Automatic rate limit handling
- 🍪 Cookie-based authentication
- ⚙️ Configurable via command line arguments or environment variables

## Installation

1. Clone this repository:

```bash
git clone https://github.com/fa0311/twitter-search-scraper.git
cd twitter-search-scraper
```

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Setup

### 1. Obtain Twitter Cookies

You need to provide Twitter authentication cookies in JSON format. Create a `cookies.json` file in the project root directory.

The cookies file should be in one of these formats:

#### Format 1: Object format

```json
{
  "auth_token": "your_auth_token_here",
  "ct0": "your_ct0_token_here"
}
```

#### Format 2: Array format (e.g., exported from browser)

```json
[
  {
    "name": "auth_token",
    "value": "your_auth_token_here"
  },
  {
    "name": "ct0",
    "value": "your_ct0_token_here"
  }
]
```

### 2. Usage

#### Basic Usage

Run the scraper with default settings (scrapes @elonmusk tweets from the last 7 days):

```bash
python -m twitter_search_scraper
```

#### Advanced Usage

Customize the scraping parameters:

```bash
python -m twitter_search_scraper \
  --screen-name "username" \
  --since "2024-01-01" \
  --until "2024-01-31" \
  --output "my_tweets.jsonl" \
  --cookies "my_cookies.json"
```

## Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--screen-name` | Twitter username to scrape (without @) | `elonmusk` |
| `--since` | Start date (YYYY-MM-DD format) | 7 days ago |
| `--until` | End date (YYYY-MM-DD format) | Today |
| `--output` | Output file path for tweets | `tweets.jsonl` |
| `--cookies` | Path to cookies JSON file | `cookies.json` |

## Output Format

The scraper saves tweets in JSONL format. Each line contains a JSON object with the following fields:

```json
{
  "username": "elonmusk",
  "url": "https://x.com/elonmusk/status/1234567890",
  "content": "Tweet content here...",
  "replyCount": 42,
  "retweetCount": 1337,
  "likeCount": 9999,
  "source": "Twitter Web App"
}
```

## Rate Limiting

The scraper automatically handles Twitter's rate limits by:

- Monitoring rate limit headers
- Automatically sleeping when limits are reached
- Resuming scraping when limits reset

## License

This project is licensed under the terms specified in the LICENSE file.
