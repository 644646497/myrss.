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
USER_AGENT = "Mozilla/5.0 (compatible; KindleEar-RSS/1.0; +https://github.com/yourusername/myrss)"

def clean_html(html):
    if not html:
        return ""
    # 清理 DW 常见无用元素
    patterns = [
        r'<div class="[^"]*?(ad|banner|related|share|recommend|footer|header|nav|cookie|social)[^"]*?".*?</div>',
        r'<aside.*?</aside>',
        r'<script.*?</script>',
        r'<style.*?</style>'
    ]
    for pattern in patterns:
        html = re.sub(pattern, '', html, flags=re.I | re.S)
    return html.strip()

def fetch_fulltext(url):
    try:
        downloaded = trafilatura.fetch_url(url, decode=True)
        if not downloaded:
            return None
            
        result = trafilatura.extract(downloaded,
                                     include_formatting=True,
                                     include_links=True,
                                     include_images=True,
                                     output_format="html",
                                     favor_recall=True)  # 更倾向抓取更多内容
        return clean_html(result) if result else None
    except Exception as e:
        print(f"全文提取失败 {url}: {e}")
        return None

def main():
    print("开始获取 DW 中文 RSS...")

    try:
        # 创建 RSS Feed
        feed = feedgenerator.Rss201rev2Feed(
            title="德国之声中文 - 全文版",
            link="https://www.dw.com/zh/",
            description="德国之声中文网全文 RSS（由 GitHub Actions 生成）",
            language="zh-CN",
            author_name="德国之声",
        )

        # 获取官方 RSS
        resp = requests.get(RSS_URL, headers={"User-Agent": USER_AGENT}, timeout=30)
        resp.raise_for_status()

        original_feed = feedparser.parse(resp.content)
        print(f"共发现 {len(original_feed.entries)} 条新闻")

        success_count = 0
        for i, entry in enumerate(original_feed.entries[:25]):   # 限制25条
            title = entry.get('title', '无标题')
            link = entry.get('link')
            if not link:
                continue

            print(f"[{i+1}/25] 处理: {title[:60]}...")

            full_content = fetch_fulltext(link)
            description = full_content if full_content else entry.get('summary', entry.get('description', ''))

            # 处理发布时间
            pub_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
            pubdate = datetime(*pub_parsed[:6]) if pub_parsed else datetime.utcnow()

            feed.add_item(
                title=title,
                link=link,
                description=description,
                pubdate=pubdate,
                unique_id=link,
            )
            success_count += 1
            time.sleep(1.5)   # 避免被封

        # 保存文件
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            feed.write(f, 'utf-8')

        print(f"✅ RSS 生成成功！共处理 {success_count} 条全文")

    except Exception as e:
        print(f"❌ 脚本执行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
