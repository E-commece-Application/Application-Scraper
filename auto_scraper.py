"""
Auto Scraper - No user input required
Scrapes from ASOS and eBay automatically
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import random
from datetime import datetime
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def create_driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def scrape_asos(driver, query, max_items=25):
    """Scrape ASOS - Works well"""
    print(f"\n[ASOS] Searching for: {query}")
    products = []
    
    try:
        url = f"https://www.asos.com/us/search/?q={query.replace(' ', '+')}"
        driver.get(url)
        time.sleep(random.uniform(3, 5))
        
        # Scroll
        for i in range(3):
            driver.execute_script(f"window.scrollTo(0, {(i+1) * 600});")
            time.sleep(0.4)
        
        items = driver.find_elements(By.CSS_SELECTOR, 'article[data-auto-id="productTile"]')
        if not items:
            items = driver.find_elements(By.CSS_SELECTOR, '[class*="productTile"]')
        
        print(f"[ASOS] Found {len(items)} items")
        
        for item in items[:max_items]:
            try:
                try:
                    name = item.find_element(By.CSS_SELECTOR, '[class*="productDescription"], h2, p').text
                except:
                    name = ""
                
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
                
                if name and len(name) > 3:
                    products.append({
                        'source': 'ASOS',
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
        print(f"[ASOS] Error: {e}")
    
    return products

def scrape_hm(driver, query, max_items=20):
    """Scrape H&M"""
    print(f"\n[H&M] Searching for: {query}")
    products = []
    
    try:
        url = f"https://www2.hm.com/en_us/search-results.html?q={query.replace(' ', '+')}"
        driver.get(url)
        time.sleep(random.uniform(4, 6))
        
        for i in range(3):
            driver.execute_script(f"window.scrollTo(0, {(i+1) * 500});")
            time.sleep(0.5)
        
        items = driver.find_elements(By.CSS_SELECTOR, '[data-item-type="product"], article.product-item')
        if not items:
            items = driver.find_elements(By.CSS_SELECTOR, '.product-item, [class*="ProductItem"]')
        
        print(f"[H&M] Found {len(items)} items")
        
        for item in items[:max_items]:
            try:
                try:
                    name = item.find_element(By.CSS_SELECTOR, 'a.link, [class*="ProductName"], h2').text
                except:
                    name = ""
                
                try:
                    price = item.find_element(By.CSS_SELECTOR, '[class*="price"], span.price').text
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
                
                if name and len(name) > 3:
                    products.append({
                        'source': 'H&M',
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
        print(f"[H&M] Error: {e}")
    
    return products

def scrape_nordstrom(driver, query, max_items=20):
    """Scrape Nordstrom"""
    print(f"\n[Nordstrom] Searching for: {query}")
    products = []
    
    try:
        url = f"https://www.nordstrom.com/sr?keyword={query.replace(' ', '+')}"
        driver.get(url)
        time.sleep(random.uniform(3, 5))
        
        for i in range(3):
            driver.execute_script(f"window.scrollTo(0, {(i+1) * 500});")
            time.sleep(0.4)
        
        items = driver.find_elements(By.CSS_SELECTOR, 'article[data-element]')
        if not items:
            items = driver.find_elements(By.CSS_SELECTOR, '[class*="ProductCard"]')
        
        print(f"[Nordstrom] Found {len(items)} items")
        
        for item in items[:max_items]:
            try:
                try:
                    name = item.find_element(By.CSS_SELECTOR, 'h2, [class*="ProductName"]').text
                except:
                    name = ""
                
                try:
                    price = item.find_element(By.CSS_SELECTOR, '[class*="Price"]').text
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
                
                if name and len(name) > 3:
                    products.append({
                        'source': 'Nordstrom',
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
        print(f"[Nordstrom] Error: {e}")
    
    return products

def scrape_forever21(driver, query, max_items=20):
    """Scrape Forever21"""
    print(f"\n[Forever21] Searching for: {query}")
    products = []
    
    try:
        url = f"https://www.forever21.com/us/shop/search/{query.replace(' ', '%20')}"
        driver.get(url)
        time.sleep(random.uniform(3, 5))
        
        for i in range(3):
            driver.execute_script(f"window.scrollTo(0, {(i+1) * 500});")
            time.sleep(0.4)
        
        items = driver.find_elements(By.CSS_SELECTOR, '.product-tile, [class*="ProductCard"]')
        print(f"[Forever21] Found {len(items)} items")
        
        for item in items[:max_items]:
            try:
                try:
                    name = item.find_element(By.CSS_SELECTOR, '[class*="product-name"], [class*="title"], h3').text
                except:
                    name = ""
                
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
                
                if name and len(name) > 3:
                    products.append({
                        'source': 'Forever21',
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
        print(f"[Forever21] Error: {e}")
    
    return products

def main():
    # Get query from command line or use default
    query = sys.argv[1] if len(sys.argv) > 1 else "shirts"
    
    print("=" * 60)
    print(f"  Auto Scraper - Query: {query}")
    print("=" * 60)
    
    print("\n[*] Starting Chrome...")
    driver = create_driver()
    
    all_products = []
    
    try:
        # Scrape multiple sites
        all_products.extend(scrape_asos(driver, query, 25))
        all_products.extend(scrape_hm(driver, query, 15))
        all_products.extend(scrape_nordstrom(driver, query, 15))
        all_products.extend(scrape_forever21(driver, query, 15))
        
    finally:
        driver.quit()
    
    # Save results
    if all_products:
        json_path = os.path.join(SCRIPT_DIR, 'clothes_data.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
        print(f"\n[+] Saved {len(all_products)} products to clothes_data.json")
    else:
        print("\n[!] No products found")
    
    print(f"\n[*] Done! Total: {len(all_products)} products")


if __name__ == "__main__":
    main()
