"""
Quick Scraper - Automatically scrapes and saves data
No user input required
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import csv
import time
import random
from datetime import datetime
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def scrape_ebay(query="t-shirts", max_items=30):
    """Scrape eBay - most reliable for scraping"""
    print(f"\n[*] Scraping eBay for: {query}")
    
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    products = []
    
    try:
        # eBay fashion category
        url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&_sacat=11450"
        print(f"[*] Loading: {url}")
        
        driver.get(url)
        time.sleep(3)
        
        # Scroll to load more
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        items = driver.find_elements(By.CSS_SELECTOR, '.s-item')
        print(f"[*] Found {len(items)} items")
        
        for item in items[1:max_items+1]:  # Skip first item (usually header)
            try:
                name = item.find_element(By.CSS_SELECTOR, '.s-item__title').text
                
                try:
                    price = item.find_element(By.CSS_SELECTOR, '.s-item__price').text
                except:
                    price = "N/A"
                
                try:
                    image = item.find_element(By.CSS_SELECTOR, '.s-item__image-img').get_attribute('src')
                except:
                    image = ""
                
                try:
                    link = item.find_element(By.CSS_SELECTOR, '.s-item__link').get_attribute('href')
                except:
                    link = ""
                
                if name and "Shop on eBay" not in name:
                    products.append({
                        'source': 'eBay',
                        'name': name,
                        'price': price,
                        'image': image,
                        'url': link,
                        'scraped_at': datetime.now().isoformat()
                    })
                    print(f"  [+] {name[:50]}...")
            except:
                continue
        
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        driver.quit()
    
    return products


def scrape_aliexpress(query="t-shirts", max_items=30):
    """Scrape AliExpress"""
    print(f"\n[*] Scraping AliExpress for: {query}")
    
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    products = []
    
    try:
        url = f"https://www.aliexpress.com/w/wholesale-{query.replace(' ', '-')}.html?catId=200000343"
        print(f"[*] Loading: {url}")
        
        driver.get(url)
        time.sleep(5)
        
        # Scroll
        for i in range(3):
            driver.execute_script(f"window.scrollTo(0, {(i+1) * 1000});")
            time.sleep(0.5)
        
        items = driver.find_elements(By.CSS_SELECTOR, '[class*="search-card-item"], [class*="product-card"], .list--gallery--C2f2tvm')
        print(f"[*] Found {len(items)} items")
        
        for item in items[:max_items]:
            try:
                try:
                    name = item.find_element(By.CSS_SELECTOR, 'h3, [class*="title"]').text
                except:
                    continue
                
                try:
                    price = item.find_element(By.CSS_SELECTOR, '[class*="price"]').text
                except:
                    price = "N/A"
                
                try:
                    image = item.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
                except:
                    image = ""
                
                try:
                    link = item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                except:
                    link = ""
                
                if name and len(name) > 5:
                    products.append({
                        'source': 'AliExpress',
                        'name': name,
                        'price': price,
                        'image': image,
                        'url': link,
                        'scraped_at': datetime.now().isoformat()
                    })
                    print(f"  [+] {name[:50]}...")
            except:
                continue
        
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        driver.quit()
    
    return products


def main():
    print("=" * 60)
    print("  Quick Clothes Scraper")
    print("=" * 60)
    
    all_products = []
    
    # Scrape eBay
    ebay_products = scrape_ebay("men shirts", 20)
    all_products.extend(ebay_products)
    
    # Scrape AliExpress
    ali_products = scrape_aliexpress("t-shirts", 20)
    all_products.extend(ali_products)
    
    # Save to JSON
    json_path = os.path.join(SCRIPT_DIR, 'clothes_data.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Saved {len(all_products)} products to {json_path}")
    
    # Save to CSV
    csv_path = os.path.join(SCRIPT_DIR, 'clothes_data.csv')
    if all_products:
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_products[0].keys())
            writer.writeheader()
            writer.writerows(all_products)
        print(f"[+] Saved {len(all_products)} products to {csv_path}")
    
    print(f"\n[*] Done! Total: {len(all_products)} products")


if __name__ == "__main__":
    main()
