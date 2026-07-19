from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

def get_dynamic_page(url, wait_selector, scroll=False):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=10000)
            page.wait_for_selector(wait_selector, timeout=10000)

            if scroll:
                for _ in range(5):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(10000)
            html = page.content()
            browser.close()
        return html
    except Exception as e:
        print(f'error: {e}')
        return None


def parse_quotes(html):
    soup = BeautifulSoup(html, "lxml")
    quote_blocks = soup.find_all("div", {"class": "quote"})
    quotes = []
    for quote in quote_blocks:
        text = quote.find("span", class_="text").get_text(strip=True)
        author = quote.find("small", class_="author").get_text(strip=True)
        tags = [
            tag.get_text(strip=True)
            for tag in quote.find("div", class_="tags").find_all("a", class_="tag")
        ]
        quotes.append({
            "text": text,
            "author": author,
            "tags": tags
        })
    return quotes



def save_to_excel(data, filename):
    pd.DataFrame(data).to_excel(filename, index=False)


if __name__ == "__main__":
    url = "https://quotes.toscrape.com/js/"
    html = get_dynamic_page(url, wait_selector=".quote", scroll=False)

    if html:
        quotes = parse_quotes(html)
        print(f"Собрано цитат: {len(quotes)}")
        save_to_excel(quotes, "quotes_js.xlsx")
    else:
        print("Не удалось загрузить страницу")