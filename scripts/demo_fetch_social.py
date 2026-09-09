"""一次性脚本: 抓YouTube(低并发重试)+ Reddit + HackerNews,给"社媒汇总"demo用。"""
import asyncio
import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

CONFIG_PATH = Path("data/config.json")
SINCE_HOURS = 72
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


async def fetch_youtube(client, sources, since):
    import feedparser
    from email.utils import parsedate_to_datetime
    import calendar

    out = []
    yt_sources = [s for s in sources if s.get("category") == "youtube" and s.get("enabled", True)]
    sem = asyncio.Semaphore(3)

    async def one(s):
        async with sem:
            await asyncio.sleep(0.4)
            try:
                resp = await client.get(s["url"], timeout=15, follow_redirects=True)
                resp.raise_for_status()
            except Exception as e:
                print(f"YT FAIL {s['name']}: {e}")
                return
            feed = feedparser.parse(resp.text)
            for entry in feed.entries[:5]:
                struct = entry.get("published_parsed")
                if not struct:
                    continue
                pub = datetime.fromtimestamp(calendar.timegm(struct), tz=timezone.utc)
                if pub < since:
                    continue
                out.append({
                    "title": entry.get("title", "Untitled"),
                    "url": entry.get("link", s["url"]),
                    "source_name": s["name"],
                    "category": "youtube",
                    "published_at": pub.isoformat(),
                })

    await asyncio.gather(*[one(s) for s in yt_sources])
    print(f"YouTube: {len(out)} 条 (from {len(yt_sources)} 频道)")
    return out


async def fetch_reddit(client, config, since):
    out = []
    for sub in config["sources"]["reddit"]["subreddits"]:
        if not sub.get("enabled", True):
            continue
        url = f"https://www.reddit.com/r/{sub['subreddit']}/hot.json?limit={sub.get('fetch_limit', 10)}"
        try:
            resp = await client.get(url, timeout=15, headers={"User-Agent": "horizon-demo/1.0"})
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"Reddit FAIL r/{sub['subreddit']}: {e}")
            continue
        for post in data.get("data", {}).get("children", []):
            p = post["data"]
            pub = datetime.fromtimestamp(p["created_utc"], tz=timezone.utc)
            if pub < since or p.get("score", 0) < sub.get("min_score", 10):
                continue
            out.append({
                "title": p["title"],
                "url": f"https://reddit.com{p['permalink']}",
                "source_name": f"r/{sub['subreddit']}",
                "category": "youtube",  # 归入"社媒"桶
                "published_at": pub.isoformat(),
            })
    print(f"Reddit: {len(out)} 条")
    return out


async def fetch_hn(client, config, since):
    out = []
    hn = config["sources"]["hackernews"]
    try:
        resp = await client.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=15)
        ids = resp.json()[:hn.get("fetch_top_stories", 30)]
    except Exception as e:
        print(f"HN FAIL: {e}")
        return out

    sem = asyncio.Semaphore(10)

    async def one(story_id):
        async with sem:
            try:
                r = await client.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=10)
                item = r.json()
            except Exception:
                return
            if not item or item.get("score", 0) < hn.get("min_score", 80):
                return
            pub = datetime.fromtimestamp(item.get("time", 0), tz=timezone.utc)
            if pub < since:
                return
            out.append({
                "title": item.get("title", "Untitled"),
                "url": item.get("url") or f"https://news.ycombinator.com/item?id={story_id}",
                "source_name": "Hacker News",
                "category": "youtube",
                "published_at": pub.isoformat(),
            })

    await asyncio.gather(*[one(i) for i in ids])
    print(f"Hacker News: {len(out)} 条")
    return out


async def main():
    config = json.loads(CONFIG_PATH.read_text())
    since = datetime.now(timezone.utc) - timedelta(hours=SINCE_HOURS)

    async with httpx.AsyncClient(headers={"User-Agent": UA}) as client:
        yt = await fetch_youtube(client, config["sources"]["rss"], since)
        reddit = await fetch_reddit(client, config, since)
        hn = await fetch_hn(client, config, since)

    items = yt + reddit + hn
    Path("data/demo_social_items.json").write_text(
        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n共 {len(items)} 条社媒内容,已存到 data/demo_social_items.json")


if __name__ == "__main__":
    asyncio.run(main())
