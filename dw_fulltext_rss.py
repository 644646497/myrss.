import requests
import feedgenerator
import feedparser
from datetime import datetime
import time
import sys

RSS_URL = "https://rss.dw.com/rdf/rss-chi-all"
OUTPUT_FILE = "feed.xml"
USER_AGENT = "Mozilla/5.0 (compatible; KindleEar-RSS/1.0)"

def main():
    print("开始获取 DW RSS...")

    try:
        feed = feedgenerator.Rss201rev2Feed(
            title="德国之声中文 - 全文版",
            link="https://www.dw.com/zh/",
            description="德国之声中文全文 RSS",
            language="zh-CN",
        )

        resp = requests.get(RSS_URL, headers={"User-Agent": USER_AGENT}, timeout=30)
        resp.raise_for_status()

        original = feedparser.parse(resp.content)
        print(f"发现 {len(original.entries)} 条新闻")

        for i, entry in enumerate(original.entries[:20]):
            title = entry.get('title', '无标题')
            link = entry.get('link')
            print(f"[{i+1}] {title[:60]}...")

            # 先尝试 Trafilatura
            full = None
            try:
                import trafilatura
                downloaded = trafilatura.fetch_url(link, decode=True)
                if downloaded:
                    full = trafilatura.extract(downloaded, include_formatting=True, 
                                             include_images=True, favor_recall=True, output_format="html")
            except:
                pass

            description = full if full and len(full) > 200 else entry.get('summary', entry.get('description', ''))

            pub_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
            pubdate = datetime(*pub_parsed[:6]) if pub_parsed else datetime.utcnow()

            feed.add_item(
                title=title,
                link=link,
                description=description,
                pubdate=pubdate,
                unique_id=link,
            )
            time.sleep(2)

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            feed.write(f, 'utf-8')

        print("✅ 生成完成")

    except Exception as e:
        print(f"❌ 出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
