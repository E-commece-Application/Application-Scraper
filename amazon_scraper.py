"""
Amazon Clothes Scraper with Selenium
-------------------------------------
Uses Selenium with undetected-chromedriver to bypass anti-bot detection.
"""

import json
import time
import random
import csv
from datetime import datetime

def install_packages():
    """Install required packages"""
    import subprocess
    import sys
    packages = ['selenium', 'webdriver-manager', 'undetected-chromedriver']
    for package in packages:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '-q'])

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    print("[*] Installing required packages...")
    install_packages()
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

# Try to use undetected-chromedriver for better anti-bot bypass
try:
    import undetected_chromedriver as uc
    USE_UNDETECTED = True
except ImportError:
    USE_UNDETECTED = False
    print("[!] undetected-chromedriver not available, using standard Chrome")


class AmazonScraper:
    def __init__(self, headless=False):
        """
        Initialize the scraper
        headless=False shows the browser (helps avoid detection)
        """
        self.products = []
        
        if USE_UNDETECTED:
            # Use undetected-chromedriver (best anti-detection)
            options = uc.ChromeOptions()
            if headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            self.driver = uc.Chrome(options=options)
        else:
            # Standard Chrome with anti-detection measures
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--window-size=1920,1080')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            
            # Remove webdriver flag
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("[+] Browser initialized successfully!")
    
    def random_delay(self, min_delay=1, max_delay=3):
        """Human-like random delay"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def human_scroll(self):
        """Scroll like a human"""
        scroll_height = self.driver.execute_script("return document.body.scrollHeight")
        current = 0
        while current < scroll_height:
            scroll_amount = random.randint(300, 700)
            current += scroll_amount
            self.driver.execute_script(f"window.scrollTo(0, {current});")
            time.sleep(random.uniform(0.3, 0.8))
    
    def scrape_amazon(self, search_query="men clothes", max_pages=2):
        """Scrape Amazon search results"""
        print(f"\n[*] Searching Amazon for: '{search_query}'")
        
        # Go to Amazon
        self.driver.get("https://www.amazon.com")
        self.random_delay(2, 4)
        
        try:
            # Find search box and enter query
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
            )
            search_box.clear()
            
            # Type like a human
            for char in search_query:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            self.random_delay(0.5, 1)
            
            # Click search button
            search_button = self.driver.find_element(By.ID, "nav-search-submit-button")
            search_button.click()
            
            self.random_delay(2, 4)
            
        except Exception as e:
            print(f"[!] Error during search: {e}")
            # Try direct URL approach
            url = f"https://www.amazon.com/s?k={search_query.replace(' ', '+')}"
            self.driver.get(url)
            self.random_delay(2, 4)
        
        # Scrape multiple pages
        for page in range(max_pages):
            print(f"\n[*] Scraping page {page + 1}...")
            
            # Scroll to load all products
            self.human_scroll()
            self.random_delay(1, 2)
            
            # Find all products
            try:
                products = self.driver.find_elements(By.CSS_SELECTOR, '[data-component-type="s-search-result"]')
                print(f"[*] Found {len(products)} products on this page")
                
                for product in products:
                    try:
                        # Get product data
                        product_data = self.extract_product_data(product)
                        if product_data and product_data['name'] != 'N/A':
                            self.products.append(product_data)
                            print(f"  [+] {product_data['name'][:60]}... - {product_data['price']}")
                    except Exception as e:
                        continue
                
            except Exception as e:
                print(f"[!] Error finding products: {e}")
            
            # Go to next page
            if page < max_pages - 1:
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, '.s-pagination-next')
                    if 's-pagination-disabled' not in next_button.get_attribute('class'):
                        next_button.click()
                        self.random_delay(2, 4)
                    else:
                        print("[*] No more pages available")
                        break
                except:
                    print("[*] Could not find next page button")
                    break
        
        return self.products
    
    def extract_product_data(self, product_element):
        """Extract data from a product element"""
        try:
            # Name
            try:
                name = product_element.find_element(By.CSS_SELECTOR, 'h2 a span').text
            except:
                name = 'N/A'
            
            # Price
            try:
                price = product_element.find_element(By.CSS_SELECTOR, '.a-price .a-offscreen').get_attribute('textContent')
            except:
                try:
                    price = product_element.find_element(By.CSS_SELECTOR, '.a-price-whole').text
                    price = f"${price}"
                except:
                    price = 'N/A'
            
            # Image
            try:
                image = product_element.find_element(By.CSS_SELECTOR, '.s-image').get_attribute('src')
            except:
                image = 'N/A'
            
            # URL
            try:
                url = product_element.find_element(By.CSS_SELECTOR, 'h2 a').get_attribute('href')
            except:
                url = 'N/A'
            
            # Rating
            try:
                rating = product_element.find_element(By.CSS_SELECTOR, '.a-icon-alt').get_attribute('textContent')
            except:
                rating = 'N/A'
            
            # Reviews count
            try:
                reviews = product_element.find_element(By.CSS_SELECTOR, '[aria-label*="stars"] + span').text
            except:
                reviews = 'N/A'
            
            return {
                'source': 'Amazon',
                'name': name,
                'price': price,
                'rating': rating,
                'reviews': reviews,
                'image': image,
                'url': url,
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            return None
    
    def export_to_json(self, filename='amazon_clothes.json'):
        """Export to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        print(f"\n[*] Exported {len(self.products)} products to {filename}")
    
    def export_to_csv(self, filename='amazon_clothes.csv'):
        """Export to CSV"""
        if not self.products:
            print("[!] No products to export")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.products[0].keys())
            writer.writeheader()
            writer.writerows(self.products)
        print(f"[*] Exported {len(self.products)} products to {filename}")
    
    def close(self):
        """Close the browser"""
        try:
            self.driver.quit()
            print("[*] Browser closed")
        except:
            pass


if __name__ == "__main__":
    print("=" * 60)
    print("  Amazon Clothes Scraper")
    print("=" * 60)
    
    # Get search query
    search_query = input("\nEnter search query (e.g., 'men t-shirts', 'women dresses'): ").strip()
    if not search_query:
        search_query = "men t-shirts"
    
    # Get number of pages
    try:
        max_pages = int(input("Number of pages to scrape (1-5, default 2): ").strip() or "2")
        max_pages = min(max(1, max_pages), 5)
    except:
        max_pages = 2
    
    print("\n[*] Starting scraper (browser will open)...")
    print("[*] Tip: Don't interact with the browser while scraping")
    
    scraper = None
    try:
        # Initialize with visible browser (less likely to be detected)
        scraper = AmazonScraper(headless=False)
        
        # Scrape
        products = scraper.scrape_amazon(search_query, max_pages)
        
        # Export
        if products:
            scraper.export_to_json()
            scraper.export_to_csv()
            print(f"\n✅ Successfully scraped {len(products)} products!")
        else:
            print("\n[!] No products found. Amazon might have blocked the request.")
            print("[*] Try running again or use a VPN.")
        
    except Exception as e:
        print(f"\n[!] Error: {e}")
    
    finally:
        if scraper:
            input("\nPress Enter to close the browser...")
            scraper.close()
