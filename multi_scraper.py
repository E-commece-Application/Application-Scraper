"""
Multi-Site Clothes Scraper
Scrapes from multiple reliable e-commerce sites
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import random
from datetime import datetime
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class MultiSiteScraper:
    def __init__(self, headless=True):
        print("[*] Setting up Chrome driver...")
        
        options = Options()
        if headless:
            options.add_argument('--headless=new')
        
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-gpu')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.products = []
        print("[+] Chrome ready!")
    
    def delay(self, min_s=1, max_s=3):
        time.sleep(random.uniform(min_s, max_s))
    
    def scroll_page(self):
        for i in range(3):
            self.driver.execute_script(f"window.scrollTo(0, {(i+1) * 500});")
            time.sleep(0.3)
    
    def scrape_ebay(self, query="shirts", max_items=25):
        """Scrape eBay - Very reliable"""
        print(f"\n[eBay] Searching for: {query}")
        
        try:
            url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&_sacat=11450"
            self.driver.get(url)
            self.delay(2, 4)
            self.scroll_page()
            
            items = self.driver.find_elements(By.CSS_SELECTOR, '.s-item')
            print(f"[eBay] Found {len(items)} items")
            
            count = 0
            for item in items[1:]:  # Skip header
                if count >= max_items:
                    break
                try:
                    name = item.find_element(By.CSS_SELECTOR, '.s-item__title').text
                    if "Shop on eBay" in name:
                        continue
                    
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
                    
                    self.products.append({
                        'source': 'eBay',
                        'name': name,
                        'price': price,
                        'image': image,
                        'url': link,
                        'scraped_at': datetime.now().isoformat()
                    })
                    count += 1
                    print(f"  [+] {name[:45]}...")
                except:
                    continue
                    
        except Exception as e:
            print(f"[eBay] Error: {e}")
    
    def scrape_etsy(self, query="vintage shirts", max_items=20):
        """Scrape Etsy - Good for unique items"""
        print(f"\n[Etsy] Searching for: {query}")
        
        try:
            url = f"https://www.etsy.com/search?q={query.replace(' ', '+')}&explicit=1&category_id=1&ship_to=US"
            self.driver.get(url)
            self.delay(3, 5)
            self.scroll_page()
            
            items = self.driver.find_elements(By.CSS_SELECTOR, '[data-listing-id]')
            print(f"[Etsy] Found {len(items)} items")
            
            count = 0
            for item in items:
                if count >= max_items:
                    break
                try:
                    try:
                        name = item.find_element(By.CSS_SELECTOR, 'h3').text
                    except:
                        name = item.find_element(By.CSS_SELECTOR, '[class*="title"]').text
                    
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
                        self.products.append({
                            'source': 'Etsy',
                            'name': name,
                            'price': price,
                            'image': image,
                            'url': link,
                            'scraped_at': datetime.now().isoformat()
                        })
                        count += 1
                        print(f"  [+] {name[:45]}...")
                except:
                    continue
                    
        except Exception as e:
            print(f"[Etsy] Error: {e}")
    
    def scrape_depop(self, query="vintage", max_items=20):
        """Scrape Depop - Fashion marketplace"""
        print(f"\n[Depop] Searching for: {query}")
        
        try:
            url = f"https://www.depop.com/search/?q={query.replace(' ', '%20')}"
            self.driver.get(url)
            self.delay(3, 5)
            self.scroll_page()
            
            items = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="product__item"]')
            if not items:
                items = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/products/"]')
            
            print(f"[Depop] Found {len(items)} items")
            
            count = 0
            for item in items:
                if count >= max_items:
                    break
                try:
                    try:
                        name = item.find_element(By.CSS_SELECTOR, '[class*="ProductCard"]').text
                    except:
                        name = "Depop Item"
                    
                    try:
                        price = item.find_element(By.CSS_SELECTOR, '[class*="price"], [class*="Price"]').text
                    except:
                        price = "N/A"
                    
                    try:
                        image = item.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
                    except:
                        image = ""
                    
                    try:
                        link = item.get_attribute('href')
                        if not link:
                            link = item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                    except:
                        link = ""
                    
                    if image:
                        self.products.append({
                            'source': 'Depop',
                            'name': name if name else "Fashion Item",
                            'price': price,
                            'image': image,
                            'url': link,
                            'scraped_at': datetime.now().isoformat()
                        })
                        count += 1
                        print(f"  [+] {name[:45]}...")
                except:
                    continue
                    
        except Exception as e:
            print(f"[Depop] Error: {e}")
    
    def scrape_shein(self, query="dresses", max_items=20):
        """Scrape Shein - Fast fashion"""
        print(f"\n[Shein] Searching for: {query}")
        
        try:
            url = f"https://us.shein.com/pdsearch/{query.replace(' ', '%20')}/"
            self.driver.get(url)
            self.delay(4, 6)
            self.scroll_page()
            self.delay(1, 2)
            
            items = self.driver.find_elements(By.CSS_SELECTOR, '.product-card, [class*="productCard"], .S-product-item')
            if not items:
                items = self.driver.find_elements(By.CSS_SELECTOR, 'section[class*="product"]')
            
            print(f"[Shein] Found {len(items)} items")
            
            count = 0
            for item in items:
                if count >= max_items:
                    break
                try:
                    try:
                        name = item.find_element(By.CSS_SELECTOR, '[class*="title"], [class*="name"], a[title]').text
                        if not name:
                            name = item.find_element(By.CSS_SELECTOR, 'a[title]').get_attribute('title')
                    except:
                        name = "Shein Item"
                    
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
                        self.products.append({
                            'source': 'Shein',
                            'name': name,
                            'price': price,
                            'image': image,
                            'url': link if link.startswith('http') else f"https://us.shein.com{link}",
                            'scraped_at': datetime.now().isoformat()
                        })
                        count += 1
                        print(f"  [+] {name[:45]}...")
                except:
                    continue
                    
        except Exception as e:
            print(f"[Shein] Error: {e}")
    
    def scrape_asos(self, query="shirts", max_items=20):
        """Scrape ASOS"""
        print(f"\n[ASOS] Searching for: {query}")
        
        try:
            url = f"https://www.asos.com/us/search/?q={query.replace(' ', '+')}"
            self.driver.get(url)
            self.delay(3, 5)
            self.scroll_page()
            
            items = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-auto-id="productTile"]')
            if not items:
                items = self.driver.find_elements(By.CSS_SELECTOR, '[class*="productTile"]')
            
            print(f"[ASOS] Found {len(items)} items")
            
            count = 0
            for item in items:
                if count >= max_items:
                    break
                try:
                    try:
                        name = item.find_element(By.CSS_SELECTOR, '[class*="productDescription"], h2, p').text
                    except:
                        name = "ASOS Item"
                    
                    try:
                        price = item.find_element(By.CSS_SELECTOR, '[class*="price"], [data-auto-id*="price"]').text
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
                        self.products.append({
                            'source': 'ASOS',
                            'name': name,
                            'price': price,
                            'image': image,
                            'url': link,
                            'scraped_at': datetime.now().isoformat()
                        })
                        count += 1
                        print(f"  [+] {name[:45]}...")
                except:
                    continue
                    
        except Exception as e:
            print(f"[ASOS] Error: {e}")
    
    def scrape_zara(self, query="shirts", max_items=15):
        """Scrape Zara"""
        print(f"\n[Zara] Searching for: {query}")
        
        try:
            url = f"https://www.zara.com/us/en/search?searchTerm={query.replace(' ', '%20')}&section=MAN"
            self.driver.get(url)
            self.delay(4, 6)
            self.scroll_page()
            
            items = self.driver.find_elements(By.CSS_SELECTOR, '[class*="product-grid-product"], li[class*="product"]')
            print(f"[Zara] Found {len(items)} items")
            
            count = 0
            for item in items:
                if count >= max_items:
                    break
                try:
                    try:
                        name = item.find_element(By.CSS_SELECTOR, '[class*="name"], [class*="product-name"], h2').text
                    except:
                        name = "Zara Item"
                    
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
                    
                    if name and len(name) > 2:
                        self.products.append({
                            'source': 'Zara',
                            'name': name,
                            'price': price,
                            'image': image,
                            'url': link,
                            'scraped_at': datetime.now().isoformat()
                        })
                        count += 1
                        print(f"  [+] {name[:45]}...")
                except:
                    continue
                    
        except Exception as e:
            print(f"[Zara] Error: {e}")
    
    def save_data(self):
        json_path = os.path.join(SCRIPT_DIR, 'clothes_data.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        print(f"\n[+] Saved {len(self.products)} products to {json_path}")
    
    def close(self):
        try:
            self.driver.quit()
        except:
            pass


def main():
    print("=" * 60)
    print("  Multi-Site Clothes Scraper")
    print("=" * 60)
    
    print("\nSelect sites to scrape:")
    print("1. eBay only")
    print("2. eBay + Etsy")
    print("3. eBay + Shein")
    print("4. eBay + ASOS")
    print("5. eBay + Zara")
    print("6. All sites (eBay, Etsy, Shein, ASOS)")
    print("7. Custom search")
    
    choice = input("\nEnter choice (1-7): ").strip()
    query = input("Search query (e.g., 'men shirts'): ").strip() or "shirts"
    
    scraper = MultiSiteScraper(headless=True)
    
    try:
        if choice == "1":
            scraper.scrape_ebay(query, 30)
        elif choice == "2":
            scraper.scrape_ebay(query, 20)
            scraper.scrape_etsy(query, 20)
        elif choice == "3":
            scraper.scrape_ebay(query, 20)
            scraper.scrape_shein(query, 20)
        elif choice == "4":
            scraper.scrape_ebay(query, 20)
            scraper.scrape_asos(query, 20)
        elif choice == "5":
            scraper.scrape_ebay(query, 20)
            scraper.scrape_zara(query, 15)
        elif choice == "6":
            scraper.scrape_ebay(query, 15)
            scraper.scrape_etsy(query, 10)
            scraper.scrape_shein(query, 10)
            scraper.scrape_asos(query, 10)
        elif choice == "7":
            print("\nWhich sites? (comma separated)")
            print("Options: ebay, etsy, shein, asos, zara, depop")
            sites = input("Sites: ").strip().lower().split(",")
            for site in sites:
                site = site.strip()
                if site == "ebay":
                    scraper.scrape_ebay(query, 20)
                elif site == "etsy":
                    scraper.scrape_etsy(query, 20)
                elif site == "shein":
                    scraper.scrape_shein(query, 20)
                elif site == "asos":
                    scraper.scrape_asos(query, 20)
                elif site == "zara":
                    scraper.scrape_zara(query, 15)
                elif site == "depop":
                    scraper.scrape_depop(query, 20)
        else:
            scraper.scrape_ebay(query, 30)
        
        if scraper.products:
            scraper.save_data()
            print(f"\n[*] Total: {len(scraper.products)} products scraped!")
        else:
            print("\n[!] No products found")
        
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
