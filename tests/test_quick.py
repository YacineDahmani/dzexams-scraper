from engine.parser import get_session, fetch_page

session = get_session()
soup = fetch_page(session, "https://www.dzexams.com/ar/4am/mathematiques/e1")

cards = soup.select("a.btn-item-sujet")
if cards:
    card = cards[0]
    print("First card full HTML:")
    print(card.prettify()[:800])
    print("\nAttributes:")
    for attr, val in card.attrs.items():
        print(f"  {attr}: {val}")
