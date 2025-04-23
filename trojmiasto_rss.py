import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import locale
import re

# Ustawiamy polskie locale dla nazw miesięcy
try:
    locale.setlocale(locale.LC_TIME, "pl_PL.UTF-8")
except locale.Error:
    pass  # nie krytyczne, jeśli się nie uda

URL = "https://www.trojmiasto.pl/wiadomosci/"

def parse_polish_date(date_str):
    # zamieniamy "22 kwietnia 2025" na datetime z UTC
    months = {
        'stycznia': '01', 'lutego': '02', 'marca': '03', 'kwietnia': '04',
        'maja': '05', 'czerwca': '06', 'lipca': '07', 'sierpnia': '08',
        'września': '09', 'października': '10', 'listopada': '11', 'grudnia': '12'
    }
    m = re.match(r'(\d{1,2})\s+(\w+)\s+(\d{4})', date_str.strip())
    if m:
        day, mon, year = m.groups()
        mm = months.get(mon.lower())
        if mm:
            dt = datetime.strptime(f"{year}-{mm}-{int(day):02d}T12:00:00", "%Y-%m-%dT%H:%M:%S")
            return dt.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc)

def fetch_articles():
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(URL, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    articles = []
    # każdy artykuł to <article class="newsList__article ...">
    for item in soup.select('article.newsList__article')[:15]:
        # tytuł i link
        a = item.select_one('h4.newsList__title a')
        title = a.get_text(strip=True)
        link = a['href']
        if link.startswith('/'):
            link = 'https://www.trojmiasto.pl' + link

        # data
        date_tag = item.select_one('span.newsList__date')
        pub_date = parse_polish_date(date_tag.get_text()) if date_tag else datetime.now(timezone.utc)

        # opis
        desc_tag = item.select_one('p.newsList__desc')
        description = desc_tag.get_text(strip=True) if desc_tag else ''

        # obrazek
        img_tag = item.select_one('div.newsList__img img')
        image = img_tag['src'] if img_tag and img_tag.has_attr('src') else ''

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
    fg.title("3city Wiadomości")
    fg.link(href=URL)
    fg.description("Najnowsze wiadomości z Trójmiasta – wygenerowane przez bota")
    fg.language('pl')

    for art in articles:
        fe = fg.add_entry()
        fe.title(art['title'])
        fe.link(href=art['link'])
        # wstawiamy obrazek jako HTML w opisie
        img_html = f'<img src="{art["image"]}" alt="" /><br>' if art['image'] else ''
        fe.description(img_html + art['description'])
        fe.pubDate(art['pubDate'])

    fg.rss_file('trojmiasto_rss.xml')
    print("Plik RSS zapisany jako trojmiasto_rss.xml")

if __name__ == "__main__":
    arts = fetch_articles()
    if not arts:
        print("UWAGA: nie znaleziono artykułów – być może zmieniła się struktura strony.")
    generate_rss(arts)