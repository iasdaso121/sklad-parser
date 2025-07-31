import logging
import requests
from bs4 import BeautifulSoup
import openpyxl
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

BASE_URL = "https://sklad-parts.ru/claas/kombain-claas/claas-dominator/?limit=100&page={}"

def parse_page(page, retries=3, delay=5):
    """Parse a single result page."""
    url = BASE_URL.format(page)
    logging.info("Fetching %s", url)
    for attempt in range(retries):
        try:
            logging.debug("Attempt %s to GET %s", attempt + 1, url)
            r = requests.get(url)
            r.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            logging.warning("Request failed on attempt %s: %s", attempt + 1, e)
            if status == 504 and attempt < retries - 1:
                logging.info("Got 504 error, retrying in %s seconds", delay)
                time.sleep(delay)
                continue
            if attempt < retries - 1:
                logging.info("Retrying in %s seconds", delay)
                time.sleep(delay)
                continue
            logging.error("Giving up on %s", url)
            raise
    soup = BeautifulSoup(r.text, "html.parser")
    results = []
    for div in soup.select("div.name"):
        a = div.find("a")
        if not a:
            continue
        text = a.get_text(strip=True)
        parts = text.split(maxsplit=1)
        article = parts[0]
        name = text
        logging.debug("Found item %s", article)
        results.append((article, name, a["href"]))
    logging.info("Parsed %d items from page %s", len(results), page)
    return results

def scrape_all():
    """Scrape all pages until no items are returned."""
    logging.info("Starting full scrape")
    page = 1
    all_items = []
    while True:
        logging.info("Scraping page %s", page)
        items = parse_page(page)
        if not items:
            logging.info("No items found on page %s", page)
            break
        all_items.extend(items)
        page += 1
    logging.info("Total items scraped: %d", len(all_items))
    return all_items

def save_to_excel(data, filename):
    """Save scraped data to an Excel file."""
    logging.info("Saving %d items to %s", len(data), filename)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Article", "Name", "URL"])
    for row in data:
        ws.append(row)
    wb.save(filename)
    logging.info("Data written to %s", filename)

if __name__ == "__main__":
    logging.info("Script started")
    data = scrape_all()
    save_to_excel(data, "output.xlsx")
    logging.info("Saved %d items to output.xlsx", len(data))