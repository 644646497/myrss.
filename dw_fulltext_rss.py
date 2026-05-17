import requests
import feedgenerator
import trafilatura
from datetime import datetime
import re
import time

# 配置
RSS_URL = "https://rss.dw.com/rdf/rss-chi-all"   # 或 rss-chi-top
OUTPUT_FILE = "feed.xml"
USER_AGENT = "Mozilla/5.0 (compatible; KindleEar-RSS/1.0)"

def clean_html(html):
    """进一步清理 DW 特有广告/导航"""
    if not html:
        return ""
    # 移除常见无用元素
    html = re.sub(r'<div class="[^"]*?(ad|banner|related|share|footer|header)[^"]*?".*?</div>', '', html, flags=re.I | re.S)
    return html

def fetch_fulltext(url):
    """提取全文"""
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return None
        
        # Trafilatura 主力提取
        result = trafilatura.extract(downloaded, 
                                   include_formatting=True,
                                   include_links=True,
                                   include_images=True,
                                   output_format="html")
        if result:
            return clean_html(result)
        
        # 备用：readability-lxml（需额外安装）
        # from readability import Document
        # doc = Document(downloaded)
        # return clean_html(doc.summary())
        
        return None
    except Exception as e:
        print(f"提取失败 {url}: {e}")
        return None

def main():
    print("Fetching DW RSS...")
    feed = feedgenerator.Rss201rev2Feed(
        title="德国之声中文 - 全文版",
        link="https://www.dw.com/zh/",
        description="德国之声中文网全文 RSS（GitHub Actions 生成）",
        language="zh-CN",
    )

    resp = requests.get(RSS_URL, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    
    import feedparser
    original_feed = feedparser.parse(resp.content)

    for entry in original_feed.entries[:30]:  # 限制数量，避免超时
        title = entry.title
        link = entry.link
        pubdate = entry.get('published_parsed') or entry.get('updated_parsed')
        
        print(f"处理: {title[:60]}...")

        full_content = fetch_fulltext(link)
        
        if full_content:
            description = full_content
        else:
            # 降级使用摘要
            description = entry.get('summary', entry.get('description', ''))
        
        feed.add_item(
            title=title,
            link=link,
            description=description,
            pubdate=datetime(*pubdate[:6]) if pubdate else datetime.now(),
            unique_id=link,
            author_name="德国之声",
        )
        
        time.sleep(1.5)  # 礼貌间隔，避免被封

    # 输出 RSS
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        feed.write(f, 'utf-8')
    
    print(f"✅ 生成完成！共 {len(original_feed.entries)} 条，已写入 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
