import logging
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_data():
    """Jalankan proses ekstraksi data."""
    logging.info("Starting extraction")
    df = scrape_main()
    logging.info(f"Total scraped data: {len(df)} rows")
    return df

def scrape_main(url_base="https://fashion-studio.dicoding.dev/page{}", max_pages=50):
    """Scraping data dari halaman website Fashion Studio.

    Args:
        url_base (str): URL template dengan placeholder untuk nomor halaman.
        max_pages (int): Jumlah maksimum halaman yang akan discrape.

    Returns:
        pd.DataFrame: DataFrame berisi title, price, rating, colors, size, gender, timestamp.

    Raises:
        requests.RequestException: Jika semua halaman gagal discrape.
    """
    data = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    errors = []

    # Halaman utama
    try:
        time.sleep(1)
        response = requests.get("https://fashion-studio.dicoding.dev/", headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        products = soup.find_all('div', class_='collection-card')
        if not products:
            logging.warning("No products found on main page")
        else:
            for product in products:
                try:
                    item = {
                        'title': product.find('h3', class_='product-title').text.strip() if product.find('h3', class_='product-title') else 'Unknown Title',
                        'price': product.find('div', class_='price-container').text.strip() if product.find('div', class_='price-container') else 'Price Not Available',
                        'rating': product.find('p', string=lambda t: t and 'Rating' in t).text.strip() if product.find('p', string=lambda t: t and 'Rating' in t) else 'No Rating',
                        'colors': product.find('p', string=lambda t: t and 'Colors' in t).text.strip() if product.find('p', string=lambda t: t and 'Colors' in t) else 'No Color Info',
                        'size': product.find('p', string=lambda t: t and 'Size' in t).text.strip() if product.find('p', string=lambda t: t and 'Size' in t) else 'No Size Info',
                        'gender': product.find('p', string=lambda t: t and 'Gender' in t).text.strip() if product.find('p', string=lambda t: t and 'Gender' in t) else 'No Gender Info',
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    data.append(item)
                except AttributeError as e:
                    logging.warning(f"Missing data in product on main page: {e}")
                    continue
            logging.info(f"Scraped main page with {len(products)} products")
    except requests.RequestException as e:
        logging.error(f"Failed to scrape main page: {e}")
        errors.append(str(e))

    # Halaman 2 sampai max_pages
    for page in range(2, max_pages + 1):
        try:
            time.sleep(1)
            page_url = url_base.format(page)
            response = requests.get(page_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            products = soup.find_all('div', class_='collection-card')
            if not products:
                logging.warning(f"No products found on page {page}")
                continue

            for product in products:
                try:
                    item = {
                        'title': product.find('h3', class_='product-title').text.strip() if product.find('h3', class_='product-title') else 'Unknown Title',
                        'price': product.find('div', class_='price-container').text.strip() if product.find('div', class_='price-container') else 'Price Not Available',
                        'rating': product.find('p', string=lambda t: t and 'Rating' in t).text.strip() if product.find('p', string=lambda t: t and 'Rating' in t) else 'No Rating',
                        'colors': product.find('p', string=lambda t: t and 'Colors' in t).text.strip() if product.find('p', string=lambda t: t and 'Colors' in t) else 'No Color Info',
                        'size': product.find('p', string=lambda t: t and 'Size' in t).text.strip() if product.find('p', string=lambda t: t and 'Size' in t) else 'No Size Info',
                        'gender': product.find('p', string=lambda t: t and 'Gender' in t).text.strip() if product.find('p', string=lambda t: t and 'Gender' in t) else 'No Gender Info',
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    data.append(item)
                except AttributeError as e:
                    logging.warning(f"Missing data in product on page {page}: {e}")
                    continue
            logging.info(f"Scraped page {page} with {len(products)} products")
        except requests.RequestException as e:
            logging.error(f"Failed to scrape page {page}: {e}")
            errors.append(str(e))
            continue

    df = pd.DataFrame(data)
    if df.empty and errors:
        raise requests.RequestException(f"All pages failed: {', '.join(errors)}")
    return df