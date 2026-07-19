import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def get_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        print(response.status_code, response.url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')
        return soup
    except requests.exceptions.Timeout:
        print('Server timed out')
        return None
    except requests.exceptions.ConnectionError:
        print('Connection error')
        return None
    except requests.exceptions.HTTPError:
        print('HTTP error')
        return None




def parse_products(soup):
    products = []
    books = soup.find_all('article', class_='product_pod')
    for book in books:
        try:
            name = book.h3.a.get('title')
            price = book.find('p', class_='price_color').text.strip()
            products.append({'name': name, 'price': price})
        except AttributeError:
            print('Attribute error')
    return products


def scrape_all_pages(base_url, max_pages=5):
    all_products = []
    for page_num in range(1, max_pages + 1):
        url = f'{base_url}page-{page_num}.html'
        soup = get_page(url)
        if soup is None:
            break

        products = parse_products(soup)
        if not products:
            break

        all_products.extend(products)
        print(f'Страница {page_num}: собрано {len(products)} товаров')
        time.sleep(1)
    return all_products



def save_to_excel(data, filename):
    pd.DataFrame(data).to_excel(filename, index=False)




if __name__ == "__main__":
    base_url = "https://books.toscrape.com/catalogue/"
    all_products = scrape_all_pages(base_url, max_pages=3)
    print(f"Собрано товаров: {len(all_products)}")
    save_to_excel(all_products, 'products1.xlsx')
    print('file started')




