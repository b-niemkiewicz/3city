import requests
from feedgen.feed import FeedGenerator
import os
from datetime import datetime
import pytz

# Ustawienie polskiej strefy czasowej
polish_tz = pytz.timezone("Europe/Warsaw")
current_time = datetime.now(polish_tz)

# Funkcja do formatowania daty w polskim formacie
def format_date(date):
    return date.strftime("%d %B %Y, %H:%M")

# Sprawdzenie, czy plik XML istnieje
if not os.path.exists("trojmiasto_rss.xml"):
    print("Plik XML nie istnieje.")
else:
    print(f"Plik XML znajduje się w: {os.path.abspath('trojmiasto_rss.xml')}")

# Twoja logika do pobierania danych
response = requests.get("https://example.com/rss_feed.xml")

if response.status_code == 200:
    print("Pobrano dane RSS!")
else:
    print("Błąd pobierania danych!")

# Generowanie pliku RSS
fg = FeedGenerator()
fg.title("Tytuł feedu")
fg.link(href="http://example.com")
fg.description("Opis feedu")

# Dodawanie wpisów do feedu
entry = fg.add_entry()
entry.title("Przykładowy tytuł")
entry.link(href="http://example.com/example-post")
entry.description("Opis wpisu")
entry.pubDate(current_time)  # Dodanie daty publikacji w polskim formacie

# Zapisz feed jako XML
fg.rss_file("trojmiasto_rss.xml")
print(f"Plik XML zapisany! {format_date(current_time)}")