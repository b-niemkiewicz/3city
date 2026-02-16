import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from email.utils import format_datetime
import xml.etree.ElementTree as ET

URL = "https://wiadomosci.trojmiasto.pl/"

def parse_polish_date(text):
    # Prosty fallback – jeśli parsowanie się nie uda,
    # używamy bieżącego czasu
    return datetime.now(timezone.utc)

def fetch_articles():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
    }

    resp = requests.get(URL, headers=headers, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    articles = []

    items = soup.select("article.newsList__article")
    print(f"DEBUG: znaleziono {len(items)} elementów")

    for idx, item in enumerate(items[:40]):

        # próbujemy kilka możliwych selektorów
        a = item.select_one("h4.newsList__title a")
        if not a:
            a = item.select_one("a[href]")

        if not a:
            print(f"DEBUG: pomijam element {idx} – brak linka")
            continue

        title = a.get_text(strip=True)
        link = a.get("href")

        if not title or not link:
            continue

        if link.startswith("/"):
            link = "https://www.trojmiasto.pl" + link

        date_tag = item.select_one("span.newsList__date")
        pub_date = parse_polish_date(date_tag.get_text(strip=True)) if date_tag else datetime.now(timezone.utc)

        desc_tag = item.select_one("p.newsList__desc")
        description = desc_tag.get_text(strip=True) if desc_tag else ""

        articles.append({
            "title": title,
            "link": link,
            "description": description,
            "pubDate": pub_date,
        })

    print(f"DEBUG: dodano {len(articles)} artykułów")
    return articles


def generate_rss(articles):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "Trojmiasto.pl - Wiadomości"
    ET.SubElement(channel, "link").text = URL
    ET.SubElement(channel, "description").text = "Najnowsze wiadomości z Trójmiasta"

    for art in articles:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = art["title"]
        ET.SubElement(item, "link").text = art["link"]
        ET.SubElement(item, "description").text = art["description"]
        ET.SubElement(item, "pubDate").text = format_datetime(art["pubDate"])

    tree = ET.ElementTree(rss)
    tree.write("trojmiasto_rss.xml", encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    arts = fetch_articles()
    generate_rss(arts)
    print("RSS wygenerowany: trojmiasto_rss.xml")
