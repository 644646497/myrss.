import requests
import feedgenerator
import feedparser
from datetime import datetime
import time

# 直接中转高质量全文 RSS
SOURCE_RSS = "https://feedx.net/rss/dw.xml"
OUTPUT_FILE = "feed.xml"

def main():
    print("正在中转 DW 全文 RSS...")

    # 获取源全文 RSS
    r = requests.get(SOURCE_RSS, timeout=30)
    r.raise_for_status()
    
    feed = feedparser.parse(r.content)

    new_feed = feedgenerator.Rss201rev2Feed(
        title="德国之声中文 - 全文版",
        link="https://www.dw.com/zh/",
        description="德国之声中文全文 RSS（GitHub 中转）",
        language="zh-CN",
    )

    for entry in feed.entries[:25]:
        new_feed.add_item(
            title=entry.title,
            link=entry.link,
            description=entry.get('content', [{}])[0].get('value') or entry.get('summary', ''),
            pubdate=datetime(*entry.published_parsed[:6]) if entry.get('published_parsed') else datetime.utcnow(),
            unique_id=entry.link,
        )

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        new_feed.write(f, 'utf-8')

    print(f"✅ 中转完成！共 {len(feed.entries)} 条")

if __name__ == "__main__":
    main()
