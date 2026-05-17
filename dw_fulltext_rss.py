import requests
import feedgenerator
import feedparser
from datetime import datetime
import time
import sys
from bs4 import BeautifulSoup

RSS_URL = "https://rss.dw.com/rdf/rss-chi-all"
OUTPUT_FILE = "feed.xml"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0 Safari/537.36"

def extract_fulltext(url):
    """尝试提取 DW 正文"""
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=25)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # DW 中文正文主要区域
        article = (soup.find('article') or 
                  soup.find('div', class_=lambda x: x and any(c in x for c in ['rich-text', 'article-content', 'dw-article', 'content'])) or
                  soup.find('div', {'id': 'bodyContent'}))
        
        if article:
            # 清理广告、相关推荐等
            for bad in article.find_all(['script', 'style', 'nav', 'aside', 'footer', 'header']):
                bad.decompose()
            for bad in article.find_all('div', class_=lambda x: x and ('ad' in x or 'related' in x or 'share' in x or 'recommend' in x)):
                bad.decompose()
            return str(article)
    except Exception as e:
        print(f"提取失败 {url}: {e}")
    return None

def main():
    print("正在生成 DW 全文 RSS...")
    
    feed = feedgenerator.Rss201rev2Feed(
        title="德国之声中文 - 全文版",
        link="https://www.dw.com/zh/",
        description="德国之声中文全文 RSS (GitHub 生成)",
        language="zh-CN",
    )

    resp = requests.get(RSS_URL, headers={"User-Agent": USER_AGENT})
    original = feedparser.parse(resp.content)

    print(f"发现 {len(original.entries)} 条新闻")

    for i, entry in enumerate(original.entries[:20]):
        title = entry.get('title', '无标题')
        link = entry.get('link')
        print(f"[{i+1}/20] 处理: {title[:60]}...")

        full_html = extract_fulltext(link)
        description = full_html if full_html and len(full_html) > 300 else entry.get('summary', entry.get('description', ''))

        pub_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
        pubdate = datetime(*pub_parsed[:6]) if pub_parsed else datetime.utcnow()

        feed.add_item(
            title=title,
            link=link,
            description=description,
            pubdate=pubdate,
            unique_id=link
        )
        time.sleep(2.5)  # 降低频率

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        feed.write(f, 'utf-8')
    
    print("✅ feed.xml 生成完成！")

if __name__ == "__main__":
    main()
