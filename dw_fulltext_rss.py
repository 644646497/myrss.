import requests
import feedgenerator
import feedparser
from datetime import datetime
import time
import sys

RSS_URL = "https://rss.dw.com/rdf/rss-chi-all"
OUTPUT_FILE = "feed.xml"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def main():
    print("开始生成 DW RSS...")

    try:
        feed = feedgenerator.Rss201rev2Feed(
            title="德国之声中文 - 全文版",
            link="https://www.dw.com/zh/",
            description="德国之声中文全文 RSS (GitHub 生成)",
            language="zh-CN",
        )

        resp = requests.get(RSS_URL, headers={"User-Agent": USER_AGENT}, timeout=20)
        original = feedparser.parse(resp.content)

        print(f"发现 {len(original.entries)} 条新闻")

        for i, entry in enumerate(original.entries[:15]):   # 减少数量，降低风险
            title = entry.get('title', '无标题')
            link = entry.get('link')
            print(f"[{i+1}/15] {title[:70]}...")

            # 直接使用官方摘要，不再尝试抓全文（避免崩溃）
            description = entry.get('summary', entry.get('description', title))

            pub_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
            pubdate = datetime(*pub_parsed[:6]) if pub_parsed else datetime.utcnow()

            feed.add_item(
                title=title,
                link=link,
                description=description,
                pubdate=pubdate,
                unique_id=link
            )
            time.sleep(1)

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            feed.write(f, 'utf-8')

        print("✅ feed.xml 生成完成（使用摘要版）")

    except Exception as e:
        print(f"❌ 脚本出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
