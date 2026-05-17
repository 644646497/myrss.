import requests
import feedgenerator
import trafilatura
import feedparser
from datetime import datetime
import re
import time
import sys

# 配置
RSS_URL = "https://rss.dw.com/rdf/rss-chi-all"
OUTPUT_FILE = "feed.xml"
USER_AGENT = "Mozilla/5.0 (compatible; KindleEar-RSS/1.0)"

def clean_html(html):
    if not html:
        return ""
    # 清理 DW 常见垃圾
    html = re.sub(r'<div class="[^"]*?(ad|banner|related|share|recommend|footer|header|nav)[^"]*?".*?</div>', '', html, flags=re.I | re.S)
    return html

def fetch_fulltext(url):
    try:
        downloaded = trafilatura.fetch_url(url, decode=True)
        if not downloaded:
            return None
        result = trafilatura.extract(downloaded,
                                     include_formatting=True,
                                     include_links=True,
                                     include_images=True,
                                     output_format="html")
        return clean_html(result) if result else None
    except Exception as e:
        print(f"全文提取失败 {url}: {e}")
        return None

def main():
    print("开始获取 DW RSS...")

    try:
        feed = feedgenerator.Rss201rev2Feed(
            title="德国之声中文 - 全文版",
            link="https://www.dw.com/zh/",
            description="德国之声中文网全文 RSS（GitHub Actions 生成）",
            language="zh-CN",
        )

        resp = requests.get(RSS_URL, headers={"User-Agent": USER_AGENT}, timeout=30)
        resp.raise_for_status()

        original_feed = feedparser.parse(resp.content)

        print(f"共发现 {len(original_feed.entries)} 条新闻")

        for i, entry in enumerate(original_feed.entries[:25]):   # 限制25条防止超时
            title = entry.title
            link = entry.link
            print(f"[{i+1}/25] 处理: {title[:50]}...")

            full_content = fetch_fulltext(link)
            description = full_content if full_content else entry.get('summary', '')

            pubdate = entry.get('published_parsed') or entry.get('updated_parsed')
            pubdate = datetime(*pubdate[:6]) if pubdate else datetime.now()

            feed.add_item(
                title=title,
                link=link,
                description=description,
                pubdate=pubdate,
                unique_id=link,
            )
            time.sleep(1.2)   # 避免请求过快

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            feed.write(f, 'utf-8')

        print(f"✅ RSS 生成成功！共处理 {len(original_feed.entries)} 条")

    except Exception as e:
        print(f"❌ 脚本执行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)   # 让 GitHub 明确显示错误

if __name__ == "__main__":
    main()
