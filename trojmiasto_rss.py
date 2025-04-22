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

def parse_polish_date(text):
    months = {
        'stycznia': 1, 'lutego': 2, 'marca': 3, 'kwietnia': 4, 'maja': 5,
        'czerwca': 6, 'lipca': 7, 'sierpnia': 8, 'września': 9,
        'października': 10, 'listopada': 11, 'grudnia': 12
    }
    parts = text.split()
    if len(parts) >= 3:
        day = int(parts[0])
        month = months.get(parts[1], 1)
        year = int(parts[2])
        return datetime(year, month, day)
    return datetime.now()

def fetch_articles():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []

    for item in soup.select('div.news-list > div')[:15]:  # ograniczamy do 15 najnowszych
        title_tag = item.select_one('h2 a')
        desc_tag = item.select_one('.short')
        img_tag = item.select_one('img')
        date_tag = item.select_one('.date')

        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = title_tag['href']
        if not link.startswith("http"):
            link = "https://www.trojmiasto.pl" + link

        description = desc_tag.get_text(strip=True) if desc_tag else ''
        image = "https://www.trojmiasto.pl" + img_tag['src'] if img_tag else ''
        pub_date = parse_polish_date(date_tag.text.strip()) if date_tag else datetime.now()

        print(f"Znaleziono artykuł: {title}")  # <-- Dodajemy print, by zobaczyć tytuły

        articles.append({
            'title': title,
            'link': link,
            'description': description,
            'image': image,
            'pubDate': pub_date,
        })

    print(f"Znaleziono {len(articles)} artykułów.")  # <-- Informacja o liczbie artykułów
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
