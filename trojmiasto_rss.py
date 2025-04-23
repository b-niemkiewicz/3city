import requests
from feedgen.feed import FeedGenerator
import os

# Sprawdzenie, czy plik XML istnieje
if not os.path.exists("trojmiasto_rss.xml"):
    print("Plik XML nie istnieje.")
else:
    print(f"Plik XML znajduje się w: {os.path.abspath('trojmiasto_rss.xml')}")

# Twoja logika do pobierania danych
response = requests.get("https://example.com/rss_feed.xml")

if response.status_code == 200:
    print("Pobrano dane RSS!")  # Dodaj to, aby zobaczyć, czy dane są pobierane
else:
    print("Błąd pobierania danych!")

# Generowanie pliku XML
fg = FeedGenerator()
fg.title("Tytuł feedu")
fg.link(href="http://example.com")
fg.description("Opis feedu")

# Dodawanie wpisów do feedu
entry = fg.add_entry()
entry.title("Przykładowy tytuł")
entry.link(href="http://example.com/example-post")
entry.description("Opis wpisu")

# Zapisz feed jako XML
fg.rss_file("trojmiasto_rss.xml")
print("Plik XML zapisany!")