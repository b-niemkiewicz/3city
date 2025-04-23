import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import pytz
import re

def fetch_and_parse_feed():
    url = "https://www.trojmiasto.pl/wiadomosci"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def parse_articles(soup):
    articles = []
    entries = soup.select("div.news-list h3 a")

    for entry in entries:
        title = entry.get_text(strip=True)
        link = "https://www.trojmiasto.pl" + entry.get("href")

        # Spróbuj wyciągnąć datę publikacji z sąsiadującego elementu
        parent = entry.find_parent("li") or entry.find_parent("article")
        date_text = parent.select_one(".news-date, .list-article__date")
        if date_text:
            pub_date = parse_polish_date(date_text.get_text(strip=True))
        else:
            pub_date = datetime.now(pytz.timezone("Europe/Warsaw"))

        articles.append({"title": title, "link": link, "pubDate": pub_date})

    return articles

def parse_polish_date(date_str):
    months = {
        "stycznia": "01", "lutego": "02", "marca": "03", "kwietnia": "04",
        "maja": "05", "czerwca": "06", "lipca": "07", "sierpnia": "08",
        "września": "09", "października": "10", "listopada": "11", "grudnia": "12"
    }

    match = re.search(r"(\d{1,2})\s+(\w+)\s+(\d{4})", date_str)
    if match:
        day, month_pl, year = match.groups()
        month = months.get(month_pl.lower())
        if month:
            dt_str = f"{year}-{month}-{int(day):02d} 12:00"
            return pytz.timezone("Europe/Warsaw").localize(datetime.strptime(dt_str, "%Y-%m-%d %H:%M"))
    return datetime.now(pytz.timezone("Europe/Warsaw"))

def generate_rss(articles):
    fg = FeedGenerator()
    fg.title("3city Wiadomości")
    fg.link(href="https://www.trojmiasto.pl/wiadomosci", rel="alternate")
    fg.description("Najnowsze wiadomości z Trójmiasta - wygenerowane przez bota")
    fg.language("pl")

    for article in articles:
        fe = fg.add_entry()
        fe.title(article["title"])
        fe.link(href=article["link"])
        fe.pubDate(article["pubDate"])

    fg.rss_file("trojmiasto_rss.xml")

def main():
    soup = fetch_and_parse_feed()
    articles = parse_articles(soup)
    generate_rss(articles)

if __name__ == "__main__":
    main()