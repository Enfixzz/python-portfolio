import requests
from bs4 import BeautifulSoup
import csv

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

def parse_countries(soup):
    country_blocks = soup.find_all("div", class_="country")
    countries = []

    for country in country_blocks:
        name = country.find("h3", class_="country-name").text.strip()
        capital = country.find("span", class_="country-capital").text.strip()

        try:
            population = float(country.find("span", class_="country-population").text.strip())
            area = float(country.find("span", class_="country-area").text.strip())
        except ValueError:
            population = 0
            area = 0

        countries.append({
            "name": name,
            "capital": capital,
            "population": population,
            "area": area
        })

    return countries

def calculate_density(countries):
    for country in countries:
        try:
            density = country["population"] / country["area"]
        except ZeroDivisionError:
            density = 0

        country["density"] = round(density, 2)

    return countries
def get_top_dense(countries, top_n=15):
    sorted_countries = sorted(
        countries,
        key=lambda country: country["density"],
        reverse=True
    )

    return sorted_countries[:top_n]

def save_to_csv(data, filename):
    fieldnames = ["name", "capital", "population", "area", "density"]

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    url = "https://www.scrapethissite.com/pages/simple/"
    soup = get_page(url)

    if soup:
        countries = parse_countries(soup)
        print(f"Собрано стран: {len(countries)}")

        countries_with_density = calculate_density(countries)
        top_dense = get_top_dense(countries_with_density, top_n=15)

        save_to_csv(top_dense, "top_dense_countries.csv")
        print("Топ-3 самых плотнонаселённых:")
        for c in top_dense[:3]:
            print(c["name"], c["density"])
    else:
        print("Не удалось загрузить страницу")