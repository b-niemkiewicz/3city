import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import locale

# Ustawienie polskiego języka dla dat (jeśli działa na Twoim systemie)
try:
    locale.setlocale(locale.LC_TIME, "pl_PL.UTF-8")
except locale.Error:
    pass  # dla GitHub Actions i Windowsa może nie działać

URL = "https://www.trojmiasto.pl/wiadomosci/"

from datetime import datetime, timezone

def parse_polish_date(date_str):
    months = {
        'stycznia': '01', 'lutego': '02', 'marca': '03', 'kwietnia': '04',
        'maja': '05', 'czerwca': '06', 'lipca': '07', 'sierpnia': '08',
        'września': '09', 'października': '10', 'listopada': '11', 'grudnia': '12'
    }

    parts = date_str.strip().split()
    if len(parts) == 3:
        day, month_name, year = parts
        month = months.get(month_name.lower())
        if month:
            dt = datetime.strptime(f"{day}.{month}.{year}", "%d.%m.%Y")
            return dt.replace(tzinfo=timezone.utc)

    return datetime.now(timezone.utc)  # fallback z UTC

def fetch_articles():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []

    # wybieramy artykuły
    for item in soup.select('article.newsList__article')[:15]:
        title_tag = item.select_one('h4.newsList__title a')
        desc_tag = item.select_one('p.newsList__desc')
        img_tag = item.select_one('div.newsList__img img')
        date_tag = item.select_one('span.newsList__date')

        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = title_tag['href']
        description = desc_tag.get_text(strip=True) if desc_tag else ''
        image = img_tag['src'] if img_tag else ''
        pub_date = parse_polish_date(date_tag.text.strip()) if date_tag else datetime.now()

        articles.append({
            'title': title,
            'link': link,
            'description': description,
            'image': image,
            'pubDate': pub_date,
        })

    print(f"Znaleziono {len(articles)} artykułów.")
    return articles


def generate_rss(articles):
    fg = FeedGenerator()
    fg.title("Trójmiasto.pl - Wiadomości")
    fg.link(href=URL)
    fg.description("Najnowsze wiadomości z Trójmiasta")
    fg.language('pl')

    for article in articles:
        fe = fg.add_entry()
        fe.title(article['title'])
        fe.link(href=article['link'])
        img_html = f'<img src="{article["image"]}" style="max-width:100%;"><br>' if article['image'] else ''
        fe.description(img_html + article['description'])
        fe.pubDate(article['pubDate'])

    fg.rss_file('trojmiasto_rss.xml')
    print("Plik RSS zapisany jako trojmiasto_rss.xml")

if __name__ == "__main__":
    articles = fetch_articles()
    generate_rss(articles)