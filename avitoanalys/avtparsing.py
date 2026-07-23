from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
]


def get_user_agent():
    return random.choice(USER_AGENTS)


def scrape_avito(search_url, max_pages=3):
    listings = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )

        context = browser.new_context(
            user_agent=get_user_agent(),
            viewport={"width": 1366, "height": 768},
            extra_http_headers={
                "Accept-Language": "ru-RU,ru;q=0.9",
                "Referer": "https://www.avito.ru/",
            }
        )

        page = context.new_page()

        for page_num in range(1, max_pages + 1):

            if page_num == 1:
                url = search_url
            else:
                url = f"{search_url}&p={page_num}"

            print(f"Парсим страницу {page_num}...")

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
                page.goto(url, wait_until="domcontentloaded")

                page.wait_for_timeout(5000)

                page.mouse.move(300, 300)
                page.mouse.wheel(0, 1500)

                page.wait_for_timeout(3000)
            except Exception as e:
                print(f"Ошибка загрузки страницы {page_num}: {e}")
                continue

            soup = BeautifulSoup(page.content(), "lxml")
            items = soup.select('[data-marker="item"]')

            print(f"Найдено {len(items)} объявлений на странице {page_num}")

            for item in items:
                title = ""
                price = ""
                location = ""
                link = ""

                title_tag = item.select_one('[itemprop="name"]')
                if title_tag:
                    title = title_tag.get_text(strip=True)

                price_tag = item.select_one('[itemprop="price"]')
                if price_tag:
                    price = price_tag.get("content", "")

                location_tag = item.select_one('[data-marker="item-location"]')
                if location_tag:
                    location = location_tag.get_text(strip=True)

                link_tag = item.find("a", href=True)
                if link_tag:
                    link = "https://www.avito.ru" + link_tag["href"]

                if title:
                    listings.append({
                        "Название": title,
                        "Цена": price,
                        "Город": location,
                        "Ссылка": link
                    })

            time.sleep(random.uniform(3, 6))

        browser.close()

    return listings


if __name__ == "__main__":
    product = "iPhone 13"
    url = f"https://www.avito.ru/moskva?q={product.replace(' ', '+')}"

    print("Начинаю парсинг...")
    data = scrape_avito(url, max_pages=2)

    if data:
        df = pd.DataFrame(data)
        print(df.head(10))
        print('n/Информация о данных:')
        print(df.info())
        df.to_excel("iphone13_avito.xlsx", index=False)
        print(f"Спарсено {len(data)} объявлений")
        print(df.head())
    else:
        print("Объявления не найдены")