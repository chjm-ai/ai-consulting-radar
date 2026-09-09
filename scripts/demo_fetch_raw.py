"""一次性脚本：轻量直连抓取(不经过orchestrator,不打分不分类),给聚类demo用。
每个源独立超时,不会被单个卡住的源拖死整体。
"""
import asyncio
import json
import sys
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import feedparser
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

CONFIG_PATH = Path("data/config.json")
SINCE_HOURS = 72
PER_REQUEST_TIMEOUT = 12
CONCURRENCY = 20

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def parse_date(entry):
    for key in ("published_parsed", "updated_parsed"):
        struct = entry.get(key)
        if struct:
            try:
                import calendar
                return datetime.fromtimestamp(calendar.timegm(struct), tz=timezone.utc)
            except Exception:
                pass
    for key in ("published", "updated"):
        raw = entry.get(key)
        if not raw:
            continue
        try:
            dt = parsedate_to_datetime(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            pass
    return None


async def fetch_one(client, sem, source, since):
    name = source["name"]
    url = source["url"]
    if not source.get("enabled", True):
        return []
    async with sem:
        try:
            resp = await client.get(url, timeout=PER_REQUEST_TIMEOUT, follow_redirects=True)
            resp.raise_for_status()
        except Exception as e:
            print(f"FAIL {name}: {e}")
            return []
        feed = feedparser.parse(resp.text)
        out = []
        for entry in feed.entries:
            pub = parse_date(entry)
            if pub is None or pub < since:
                continue
            out.append({
                "title": entry.get("title", "Untitled"),
                "url": entry.get("link", url),
                "source_name": name,
                "category": source.get("category"),
                "published_at": pub.isoformat(),
            })
        return out


async def main():
    config = json.loads(CONFIG_PATH.read_text())
    sources = config["sources"]["rss"]
    since = datetime.now(timezone.utc) - timedelta(hours=SINCE_HOURS)

    sem = asyncio.Semaphore(CONCURRENCY)
    async with httpx.AsyncClient(headers={"User-Agent": UA}) as client:
        results = await asyncio.gather(
            *[fetch_one(client, sem, s, since) for s in sources]
        )

    items = [item for group in results for item in group]
    Path("data/demo_raw_items.json").write_text(
        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n共抓到 {len(items)} 条 (近{SINCE_HOURS}小时), 已存到 data/demo_raw_items.json")


if __name__ == "__main__":
    asyncio.run(main())
