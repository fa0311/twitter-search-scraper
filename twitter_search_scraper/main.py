import json
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Callable, Generator

from pydantic import validate_call
from pydantic_settings import BaseSettings, SettingsConfigDict
from twitter_openapi_python import (
    TweetApiUtilsData,
    TwitterOpenapiPython,
    TwitterOpenapiPythonClient,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(cli_parse_args=True)
    cookies: Path = Path("cookies.json")
    output: Path = Path("tweets.jsonl")
    screen_name: str = "elonmusk"
    until: date = date.today()
    since: date = date.today() - timedelta(days=7)

    def __init__(self, **data):
        super().__init__(**data)


@validate_call(validate_return=True)
def get_cookies(path: Path) -> dict[str, str]:
    with open(path, "r") as f:
        cookies = json.load(f)
    if isinstance(cookies, list):
        cookies = {cookie["name"]: cookie["value"] for cookie in cookies}
    return cookies


def to_url(screen_name: str, rest_id: str) -> str:
    return f"https://x.com/{screen_name}/status/{rest_id}"


def get_search_timeline(
    twitter: TwitterOpenapiPythonClient,
    query: str,
    until: date,
    since: date,
    logger: Callable = print,
    sleep: Callable[[float], None] = time.sleep,
) -> Generator[TweetApiUtilsData, None, None]:
    last_cursor: str | None = None
    while True:
        response = twitter.get_tweet_api().get_search_timeline(
            raw_query=f"{query} until:{until} since:{since}",
            product="Latest",
            cursor=last_cursor,
            count=20,
        )

        logger(f"Fetched {len(response.data.data)} tweets")

        if len(response.data.data) == 0:
            return None

        for tweet in response.data.data:
            if tweet.promoted_metadata is not None:
                continue
            yield tweet

        if response.data.cursor.bottom is None:
            return None
        else:
            last_cursor = response.data.cursor.bottom.value
        logger(f"Next cursor: {last_cursor}")

        if response.header.rate_limit_remaining == 0:
            rate_limit_reset = datetime.fromtimestamp(response.header.rate_limit_reset)
            sleep_seconds = (rate_limit_reset - datetime.now()).total_seconds() + 10
            logger(f"Rate limit reached. Sleeping for {sleep_seconds} seconds.")
            sleep(sleep_seconds)


def main():
    cli = Settings()
    cookies = get_cookies(cli.cookies)
    twitter = TwitterOpenapiPython().get_client_from_cookies(cookies=cookies)
    tweets = get_search_timeline(
        twitter=twitter,
        query=f"from:{cli.screen_name}",
        until=cli.until,
        since=cli.since,
        logger=print,
        sleep=time.sleep,
    )

    print(f"{cli.model_dump_json()}")

    with open(cli.output, "w", encoding="utf-8") as f:
        for tweet in tweets:
            if legacy := tweet.tweet.legacy:
                data = {
                    "username": tweet.user.legacy.screen_name,
                    "url": to_url(tweet.user.legacy.screen_name, tweet.tweet.rest_id),
                    "content": legacy.full_text,
                    "replyCount": legacy.reply_count,
                    "retweetCount": legacy.retweet_count,
                    "likeCount": legacy.favorite_count,
                    "source": tweet.tweet.source,
                }
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
