import feedparser
import requests
from bs4 import BeautifulSoup
import random
import os
from typing import Dict, Optional


# ==================== ニュースソース取得関数 ====================

def get_economist() -> Optional[Dict]:
    """The EconomistのビジネスセクションからRSSで最新記事を取得"""
    try:
        url = "https://www.economist.com/business/rss.xml"
        feed = feedparser.parse(url)
        if feed.entries:
            return {
                "source": "The Economist",
                "title": feed.entries[0].title,
                "link": feed.entries[0].link
            }
        return None
    except Exception as e:
        print(f"Error fetching The Economist: {e}")
        return None

def get_mit_tech_review() -> Optional[Dict]:
    """MIT Technology ReviewからRSSで最新記事を取得"""
    try:
        url = "https://www.technologyreview.com/feed/"
        feed = feedparser.parse(url)
        if feed.entries:
            return {
                "source": "MIT Tech Review",
                "title": feed.entries[0].title,
                "link": feed.entries[0].link
            }
        return None
    except Exception as e:
        print(f"Error fetching MIT Tech Review: {e}")
        return None


def get_morning_brew() -> Optional[Dict]:
    """Morning Brewから最新記事をスクレイピングで取得"""
    try:
        url = "https://www.morningbrew.com/daily/latest"
        headers = {"User-Agent": "Mozilla/5.0"}  # ブラウザのふりをする
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        latest_article = soup.find("h1") or soup.select_one("a[class*='article']")
        
        if latest_article:
            return {
                "source": "Morning Brew",
                "title": latest_article.text.strip(),
                "link": "https://www.morningbrew.com" + latest_article['href']
            }
        return None
    except Exception as e:
        print(f"Error fetching Morning Brew: {e}")
        return None


def get_ground_news() -> Optional[Dict]:
    """Ground NewsからRSSで最新見出しを取得"""
    try:
        url = "https://groundnews.com/feed"
        feed = feedparser.parse(url)
        if feed.entries:
            return {
                "source": "Ground News",
                "title": feed.entries[0].title,
                "link": feed.entries[0].link
            }
        return None
    except Exception as e:
        print(f"Error fetching Ground News: {e}")
        return None


# ==================== Slack連携機能 ====================

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def send_to_slack(article: Dict) -> None:
    """記事をSlackに送信"""
    if not SLACK_WEBHOOK_URL:
        print("Warning: SLACK_WEBHOOK_URL is not set. Skipping Slack notification.")
        return

    try:
        payload = {
            "text": f"【今日の思考テーマ】\n*Source:* {article['source']}\n*Title:* {article['title']}\n*URL:* {article['link']}\n\n"
                    f"1. この記事の前提は何か？\n2. 逆の視点はないか？\n3. 自分のキャリアにどう繋がるか？"
        }
        requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        print("✓ Slack notification sent successfully")
    except Exception as e:
        print(f"Error sending to Slack: {e}")


# ==================== ニュース選択・表示機能 ====================

def pick_daily_news(send_slack: bool = False) -> None:
    """登録されたニュースソースからランダムに1件を選択して表示
    
    Args:
        send_slack: Slackに送信する場合はTrue
    """
    sources = [
        get_economist,
        get_mit_tech_review,
        get_morning_brew,
        get_ground_news
    ]
    
    # 複数回試行して有効な結果を取得
    for _ in range(len(sources)):
        selected = random.choice(sources)()
        if selected:
            display_news(selected)
            if send_slack:
                send_to_slack(selected)
            return
    
    print("Error: Could not fetch news from any source")


def display_news(article: Dict) -> None:
    """ニュース記事をフォーマットして表示"""
    print(f"--- Today's Thinking Theme ---")
    print(f"Source: {article['source']}")
    print(f"Title : {article['title']}")
    print(f"URL   : {article['link']}")


# pickup_news.py の一番下をこれに書き換え
if __name__ == "__main__":
    # 環境変数が設定されていればSlack送信を有効にする
    send_flag = True if os.getenv("SLACK_WEBHOOK_URL") else False
    pick_daily_news(send_slack=send_flag)