import requests
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

URL = "https://www.trojmiasto.pl/wiadomosci/rss.xml"

def format_polish_date(date):
    months = {
        1: "stycznia", 2: "lutego", 3: "marca", 4: "kwietnia",
        5: "maja", 6: "czerwca", 7: "lipca", 8: "sierpnia",
        9: "września", 10: "października", 11: "listopada", 12: "grudnia"
    }
    return f"{date.day} {months[date.month]} {date.year}, {date.strftime('%H:%M')}"

def fetch_and_parse_feed():
    response = requests.get(URL)
    response.raise_for_status()
    return BeautifulSoup(response.content, features="xml")

def generate_feed(items):
    fg = FeedGenerator()
    fg.id("https://www.trojmiasto.pl/")
    fg.title("Wiadomości Trójmiasto.pl")
    fg.link(href="https://www.trojmiasto.pl/", rel="alternate")
    fg.language("pl")
    fg.description("Automatycznie aktualizowany RSS z Trójmiasto.pl")

    for item in items:
        fe = fg.add_entry()
        fe.id(item.guid.text)
        fe.title(item.title.text)
        fe.link(href=item.link.text)
        fe.description(item.description.text)
        pub_date = datetime.strptime(item.pubDate.text, "%a, %d %b %Y %H:%M:%S %z")
        fe.pubDate(pub_date)

    return fg

def main():
    soup = fetch_and_parse_feed()
    items = soup.find_all("item")

    fg = generate_feed(items)
    fg.rss_file("trojmiasto_rss.xml")

    print("Zapisano trojmiasto_rss.xml")
    print("Data aktualizacji:", format_polish_date(datetime.now(pytz.timezone("Europe/Warsaw"))))

if __name__ == "__main__":
    main()