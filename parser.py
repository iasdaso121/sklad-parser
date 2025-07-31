import requests
from bs4 import BeautifulSoup
import openpyxl

BASE_URL = "https://sklad-parts.ru/claas/kombain-claas/claas-dominator/?limit=100&page={}"

def parse_page(page):
    url = BASE_URL.format(page)
    r = requests.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    results = []
    for div in soup.select('div.name'):
        a = div.find('a')
        if not a:
            continue
        text = a.get_text(strip=True)
        # Article is numeric prefix
        parts = text.split(maxsplit=1)
        article = parts[0]
        name = text
        results.append((article, name, a['href']))
    return results

def scrape_all():
    page = 1
    all_items = []
    while True:
        items = parse_page(page)
        if not items:
            break
        all_items.extend(items)
        page += 1
    return all_items

def save_to_excel(data, filename):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Article", "Name", "URL"])
    for row in data:
        ws.append(row)
    wb.save(filename)

if __name__ == "__main__":
    data = scrape_all()
    save_to_excel(data, "output.xlsx")
    print(f"Saved {len(data)} items to output.xlsx")