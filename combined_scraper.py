"""
Combined Multi-Site Scraper
Scrapes from ASOS + AliExpress + eBay together
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

def scroll_page(driver):
    for i in range(3):
        driver.execute_script(f"window.scrollTo(0, {(i+1) * 600});")
        time.sleep(0.4)

def scrape_asos(driver, query, max_items=15):
    """Scrape ASOS"""
    print(f"\n[ASOS] Searching for: {query}")
    products = []
    
    try:
        url = f"https://www.asos.com/us/search/?q={query.replace(' ', '+')}"
        driver.get(url)
        time.sleep(random.uniform(3, 5))
        scroll_page(driver)
        
        items = driver.find_elements(By.CSS_SELECTOR, 'article[data-auto-id="productTile"]')
        if not items:
            items = driver.find_elements(By.CSS_SELECTOR, '[class*="productTile"]')
        
        print(f"[ASOS] Found {len(items)} items")
        
        for item in items[:max_items]:
            try:
                name = item.find_element(By.CSS_SELECTOR, '[class*="productDescription"], h2, p').text
                price = item.find_element(By.CSS_SELECTOR, '[class*="price"]').text if item.find_elements(By.CSS_SELECTOR, '[class*="price"]') else "N/A"
                image = item.find_element(By.CSS_SELECTOR, 'img').get_attribute('src') if item.find_elements(By.CSS_SELECTOR, 'img') else ""
                link = item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href') if item.find_elements(By.CSS_SELECTOR, 'a') else ""
                
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

def scrape_aliexpress(driver, query, max_items=15):
    """Scrape AliExpress"""
    print(f"\n[AliExpress] Searching for: {query}")
    products = []
    
    try:
        url = f"https://www.aliexpress.com/w/wholesale-{query.replace(' ', '-')}.html?catId=200000343"
        driver.get(url)
        time.sleep(random.uniform(4, 6))
        scroll_page(driver)
        time.sleep(1)
        
        items = driver.find_elements(By.CSS_SELECTOR, '[class*="search-card-item"], [class*="product-card"], .list--gallery--C2f2tvm')
        print(f"[AliExpress] Found {len(items)} items")
        
        for item in items[:max_items]:
            try:
                try:
                    name = item.find_element(By.CSS_SELECTOR, 'h3, [class*="title"]').text
                except:
                    continue
                
                price = item.find_element(By.CSS_SELECTOR, '[class*="price"]').text if item.find_elements(By.CSS_SELECTOR, '[class*="price"]') else "N/A"
                image = item.find_element(By.CSS_SELECTOR, 'img').get_attribute('src') if item.find_elements(By.CSS_SELECTOR, 'img') else ""
                link = item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href') if item.find_elements(By.CSS_SELECTOR, 'a') else ""
                
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
        print(f"[AliExpress] Error: {e}")
    
    return products

def scrape_ebay(driver, query, max_items=15):
    """Scrape eBay"""
    print(f"\n[eBay] Searching for: {query}")
    products = []
    
    try:
        url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&_sacat=11450"
        driver.get(url)
        time.sleep(random.uniform(2, 4))
        scroll_page(driver)
        
        items = driver.find_elements(By.CSS_SELECTOR, '.s-item')
        print(f"[eBay] Found {len(items)} items")
        
        count = 0
        for item in items[1:]:  # Skip header
            if count >= max_items:
                break
            try:
                name = item.find_element(By.CSS_SELECTOR, '.s-item__title').text
                if "Shop on eBay" in name:
                    continue
                
                price = item.find_element(By.CSS_SELECTOR, '.s-item__price').text if item.find_elements(By.CSS_SELECTOR, '.s-item__price') else "N/A"
                image = item.find_element(By.CSS_SELECTOR, '.s-item__image-img').get_attribute('src') if item.find_elements(By.CSS_SELECTOR, '.s-item__image-img') else ""
                link = item.find_element(By.CSS_SELECTOR, '.s-item__link').get_attribute('href') if item.find_elements(By.CSS_SELECTOR, '.s-item__link') else ""
                
                products.append({
                    'source': 'eBay',
                    'name': name,
                    'price': price,
                    'image': image,
                    'url': link,
                    'scraped_at': datetime.now().isoformat()
                })
                count += 1
                print(f"  [+] {name[:50]}...")
            except:
                continue
                
    except Exception as e:
        print(f"[eBay] Error: {e}")
    
    return products

def scrape_shein(driver, query, max_items=10):
    """Scrape Shein"""
    print(f"\n[Shein] Searching for: {query}")
    products = []
    
    try:
        url = f"https://us.shein.com/pdsearch/{query.replace(' ', '%20')}/"
        driver.get(url)
        time.sleep(random.uniform(4, 6))
        scroll_page(driver)
        
        items = driver.find_elements(By.CSS_SELECTOR, '.product-card, [class*="productCard"], .S-product-item')
        print(f"[Shein] Found {len(items)} items")
        
        for item in items[:max_items]:
            try:
                try:
                    name = item.find_element(By.CSS_SELECTOR, '[class*="title"], [class*="name"], a[title]').text
                    if not name:
                        name = item.find_element(By.CSS_SELECTOR, 'a[title]').get_attribute('title')
                except:
                    name = ""
                
                price = item.find_element(By.CSS_SELECTOR, '[class*="price"]').text if item.find_elements(By.CSS_SELECTOR, '[class*="price"]') else "N/A"
                image = item.find_element(By.CSS_SELECTOR, 'img').get_attribute('src') if item.find_elements(By.CSS_SELECTOR, 'img') else ""
                link = item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href') if item.find_elements(By.CSS_SELECTOR, 'a') else ""
                
                if name and len(name) > 3:
                    products.append({
                        'source': 'Shein',
                        'name': name,
                        'price': price,
                        'image': image,
                        'url': link if link.startswith('http') else f"https://us.shein.com{link}",
                        'scraped_at': datetime.now().isoformat()
                    })
                    print(f"  [+] {name[:50]}...")
            except:
                continue
                
    except Exception as e:
        print(f"[Shein] Error: {e}")
    
    return products

def main():
    query = sys.argv[1] if len(sys.argv) > 1 else "t-shirts"
    
    print("=" * 60)
    print(f"  Combined Multi-Site Scraper")
    print(f"  Query: {query}")
    print("=" * 60)
    
    print("\n[*] Starting Chrome...")
    driver = create_driver()
    
    all_products = []
    
    try:
        # Scrape from all sites
        all_products.extend(scrape_asos(driver, query, 15))
        all_products.extend(scrape_aliexpress(driver, query, 15))
        all_products.extend(scrape_ebay(driver, query, 15))
        all_products.extend(scrape_shein(driver, query, 10))
        
    finally:
        driver.quit()
    
    # Save results
    if all_products:
        json_path = os.path.join(SCRIPT_DIR, 'clothes_data.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
        
        # Count by source
        sources = {}
        for p in all_products:
            src = p['source']
            sources[src] = sources.get(src, 0) + 1
        
        print(f"\n{'=' * 40}")
        print(f"[+] Saved {len(all_products)} products total:")
        for src, count in sources.items():
            print(f"    - {src}: {count} products")
        print(f"{'=' * 40}")
    else:
        print("\n[!] No products found")


if __name__ == "__main__":
    main()
