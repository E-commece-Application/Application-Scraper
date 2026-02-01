"""
Smart Clothes Scraper - Auto-detects Chrome version
Uses webdriver-manager to automatically download correct ChromeDriver
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

class SmartClothingScraper:
    def __init__(self, headless=False):
        """Initialize with auto-detected ChromeDriver"""
        print("[*] Setting up Chrome driver (auto-detecting version)...")
        
        options = Options()
        
        if headless:
            options.add_argument('--headless=new')
        
        # Anti-detection settings
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-infobars')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36')
        
        # Disable automation flags
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Use webdriver-manager to auto-download correct driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Remove webdriver flag
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            '''
        })
        
        self.products = []
        print("[+] Chrome driver ready!")
    
    def random_delay(self, min_sec=2, max_sec=4):
        """Human-like random delay"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def scroll_page(self):
        """Scroll page to load lazy content"""
        scroll_pause = 0.5
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for i in range(3):
            self.driver.execute_script(f"window.scrollTo(0, {(i+1) * last_height / 3});")
            time.sleep(scroll_pause)
        
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)
    
    def scrape_amazon(self, search_query, max_pages=2):
        """Scrape Amazon clothing"""
        print(f"\n[*] Searching Amazon for: {search_query}")
        
        base_url = f"https://www.amazon.com/s?k={search_query.replace(' ', '+')}&i=fashion"
        
        for page in range(1, max_pages + 1):
            url = f"{base_url}&page={page}"
            print(f"[*] Page {page}/{max_pages}...")
            
            try:
                self.driver.get(url)
                self.random_delay(3, 5)
                self.scroll_page()
                
                # Wait for products
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-component-type="s-search-result"]'))
                )
                
                products = self.driver.find_elements(By.CSS_SELECTOR, '[data-component-type="s-search-result"]')
                print(f"    Found {len(products)} items on this page")
                
                for product in products:
                    try:
                        # Get product name
                        try:
                            name = product.find_element(By.CSS_SELECTOR, 'h2 span').text
                        except:
                            name = "N/A"
                        
                        # Get price
                        try:
                            price = product.find_element(By.CSS_SELECTOR, '.a-price .a-offscreen').get_attribute('textContent')
                        except:
                            try:
                                price = product.find_element(By.CSS_SELECTOR, '.a-price-whole').text
                                price = f"${price}"
                            except:
                                price = "N/A"
                        
                        # Get image
                        try:
                            image = product.find_element(By.CSS_SELECTOR, '.s-image').get_attribute('src')
                        except:
                            image = "N/A"
                        
                        # Get link
                        try:
                            link = product.find_element(By.CSS_SELECTOR, 'h2 a').get_attribute('href')
                        except:
                            link = "N/A"
                        
                        # Get rating
                        try:
                            rating = product.find_element(By.CSS_SELECTOR, '.a-icon-alt').get_attribute('textContent')
                        except:
                            rating = "N/A"
                        
                        if name and name != "N/A":
                            self.products.append({
                                'source': 'Amazon',
                                'name': name,
                                'price': price,
                                'rating': rating,
                                'image': image,
                                'url': link,
                                'scraped_at': datetime.now().isoformat()
                            })
                            print(f"    [+] {name[:50]}...")
                    
                    except Exception as e:
                        continue
                
                self.random_delay(2, 4)
                
            except Exception as e:
                print(f"    [!] Error on page {page}: {str(e)[:50]}")
        
        return self.products
    
    def scrape_ebay(self, search_query, max_pages=2):
        """Scrape eBay clothing"""
        print(f"\n[*] Searching eBay for: {search_query}")
        
        for page in range(1, max_pages + 1):
            url = f"https://www.ebay.com/sch/i.html?_nkw={search_query.replace(' ', '+')}&_sacat=11450&_pgn={page}"
            print(f"[*] Page {page}/{max_pages}...")
            
            try:
                self.driver.get(url)
                self.random_delay(2, 4)
                self.scroll_page()
                
                products = self.driver.find_elements(By.CSS_SELECTOR, '.s-item')
                print(f"    Found {len(products)} items")
                
                for product in products[1:]:  # Skip first (it's usually a header)
                    try:
                        name = product.find_element(By.CSS_SELECTOR, '.s-item__title').text
                        
                        try:
                            price = product.find_element(By.CSS_SELECTOR, '.s-item__price').text
                        except:
                            price = "N/A"
                        
                        try:
                            image = product.find_element(By.CSS_SELECTOR, '.s-item__image-img').get_attribute('src')
                        except:
                            image = "N/A"
                        
                        try:
                            link = product.find_element(By.CSS_SELECTOR, '.s-item__link').get_attribute('href')
                        except:
                            link = "N/A"
                        
                        if name and "Shop on eBay" not in name:
                            self.products.append({
                                'source': 'eBay',
                                'name': name,
                                'price': price,
                                'image': image,
                                'url': link,
                                'scraped_at': datetime.now().isoformat()
                            })
                            print(f"    [+] {name[:50]}...")
                    
                    except:
                        continue
                
                self.random_delay(2, 3)
                
            except Exception as e:
                print(f"    [!] Error: {e}")
        
        return self.products
    
    def scrape_aliexpress(self, search_query, max_pages=1):
        """Scrape AliExpress clothing"""
        print(f"\n[*] Searching AliExpress for: {search_query}")
        
        url = f"https://www.aliexpress.com/w/wholesale-{search_query.replace(' ', '-')}.html?catId=200000343"
        print(f"[*] Loading page...")
        
        try:
            self.driver.get(url)
            self.random_delay(4, 6)
            self.scroll_page()
            self.random_delay(2, 3)
            
            # Find product cards
            products = self.driver.find_elements(By.CSS_SELECTOR, '[class*="search-card-item"], [class*="product-card"]')
            print(f"    Found {len(products)} items")
            
            for product in products[:30]:  # Limit to 30
                try:
                    try:
                        name = product.find_element(By.CSS_SELECTOR, 'h3, [class*="title"]').text
                    except:
                        name = "N/A"
                    
                    try:
                        price = product.find_element(By.CSS_SELECTOR, '[class*="price"]').text
                    except:
                        price = "N/A"
                    
                    try:
                        image = product.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
                    except:
                        image = "N/A"
                    
                    try:
                        link = product.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                    except:
                        link = "N/A"
                    
                    if name and name != "N/A" and len(name) > 5:
                        self.products.append({
                            'source': 'AliExpress',
                            'name': name,
                            'price': price,
                            'image': image,
                            'url': link,
                            'scraped_at': datetime.now().isoformat()
                        })
                        print(f"    [+] {name[:50]}...")
                
                except:
                    continue
            
        except Exception as e:
            print(f"    [!] Error: {e}")
        
        return self.products
    
    def export_json(self, filename='clothes_data.json'):
        """Export to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        print(f"\n[+] Saved {len(self.products)} products to {filename}")
    
    def export_csv(self, filename='clothes_data.csv'):
        """Export to CSV"""
        if not self.products:
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.products[0].keys())
            writer.writeheader()
            writer.writerows(self.products)
        print(f"[+] Saved {len(self.products)} products to {filename}")
    
    def close(self):
        """Close browser"""
        try:
            self.driver.quit()
        except:
            pass


def main():
    print("=" * 60)
    print("  Smart Clothes Scraper")
    print("=" * 60)
    
    print("\nSelect site to scrape:")
    print("1. Amazon")
    print("2. eBay")
    print("3. AliExpress")
    print("4. All sites")
    
    choice = input("\nEnter choice (1-4): ").strip()
    query = input("Search query (e.g., 'men shirts'): ").strip() or "men shirts"
    
    try:
        pages = int(input("Pages to scrape (1-3, default 2): ").strip() or "2")
        pages = min(max(pages, 1), 3)
    except:
        pages = 2
    
    headless = input("Run headless (no browser window)? (y/n, default n): ").strip().lower() == 'y'
    
    try:
        scraper = SmartClothingScraper(headless=headless)
        
        if choice == "1":
            scraper.scrape_amazon(query, pages)
        elif choice == "2":
            scraper.scrape_ebay(query, pages)
        elif choice == "3":
            scraper.scrape_aliexpress(query, 1)
        elif choice == "4":
            scraper.scrape_amazon(query, pages)
            scraper.scrape_ebay(query, pages)
            scraper.scrape_aliexpress(query, 1)
        else:
            print("[!] Invalid choice")
            scraper.close()
            return
        
        if scraper.products:
            scraper.export_json()
            scraper.export_csv()
            print(f"\n[*] Total: {len(scraper.products)} products scraped!")
        else:
            print("\n[!] No products found")
        
        scraper.close()
        
    except Exception as e:
        print(f"\n[!] Error: {e}")
        print("\n[?] Troubleshooting:")
        print("    1. Make sure Google Chrome is installed")
        print("    2. Try running: pip install --upgrade webdriver-manager selenium")


if __name__ == "__main__":
    main()
