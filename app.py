import snscrape.modules.twitter as snstwitter
import pandas as pd 
import os
import certifi
import ssl
import urllib.request

os.environ['SSL_CERT_FILE'] = certifi.where() 


# naukri, jobs, jobseeker, vacancy
hashtags = "(#naukri OR #jobs OR #jobseeker OR #vacancy) lang:en since:2022-01-01 until:2022-05-31"

tweets = []

for i,tweet in enumerate(snstwitter.TwitterSearchScraper(hashtags).get_items()):
    if i >= 2000:
        break
    tweets.append([
        tweet.user.username,
        tweet.date.date(),
        tweet.date.time(),
        tweet.rawContent,
        [mention.username for mention in tweet.mentionedUsers] if tweet.mentionedUsers else [],
        [hashtag for hashtag in tweet.hashtags] if tweet.hashtags else [],
        tweet.likeCount,
        tweet.retweetCount,
        tweet.replyCount,
        tweet.viewCount,
    ])


tweets.to_csv("Tweet_extract.csv",index=False)
print("Data extracted successfully")

# 2nd attempt


from ntscraper import Nitter

scrapper = Nitter()
scrapper.instances = [
    "https://nitter.poast.org",
    "https://nitter.lacontrevoie.fr",
    "https://nitter.1d4.us"
]

tweets = scrapper.get_tweets("naukri", mode="hashtag", number=2000,)

print(f"Fetched {len(tweets['tweets'])} tweets.")

# 3rd attempt
import asyncio
from playwright.async_api import async_playwright
import csv

# Customize here
HASHTAG = "naukri"
MAX_TWEETS = 2000
OUTPUT_FILE = "naukri_tweets.csv"

async def run():
    tweet_data = set()  # Use set to avoid duplicates

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        search_url = f"https://twitter.com/search?q=%23{HASHTAG}&src=typed_query&f=live"
        await page.goto(search_url)

        last_height = 0
        scrolls = 0

        while len(tweet_data) < MAX_TWEETS:
            # Wait for tweets to load
            await page.wait_for_timeout(2000)

            tweets = await page.locator('article').all()
            for tweet in tweets:
                try:
                    content = await tweet.inner_text()
                    tweet_data.add(content.strip())
                    if len(tweet_data) >= MAX_TWEETS:
                        break
                except:
                    continue

            await page.keyboard.press("PageDown")
            scrolls += 1

            # Optional: Stop if no new tweets found after several scrolls
            if scrolls > 100:
                break

        print(f"\n✅ Total tweets scraped: {len(tweet_data)}")

        # Save to CSV
        with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Tweet"])
            for tweet in tweet_data:
                writer.writerow([tweet])

        print(f"📁 Saved to {OUTPUT_FILE}")
        await browser.close()

asyncio.run(run())
