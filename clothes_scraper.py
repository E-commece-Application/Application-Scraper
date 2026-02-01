"""
E-Commerce Clothes Scraper
--------------------------
This script scrapes clothing data from e-commerce websites.
It includes anti-bot detection measures like random delays, rotating user agents, and session handling.

DISCLAIMER: Make sure to check the website's robots.txt and Terms of Service before scraping.
Use responsibly and respect rate limits.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
import csv
from datetime import datetime
from fake_useragent import UserAgent
from urllib.parse import urljoin, urlparse
import re

class ClothingScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.products = []
        
        # Rotate between different user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
    
    def get_headers(self):
        """Generate realistic browser headers"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
    
    def random_delay(self, min_delay=2, max_delay=5):
        """Add random delay to mimic human behavior"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def make_request(self, url, retries=3):
        """Make a request with retry logic and anti-bot measures"""
        for attempt in range(retries):
            try:
                self.random_delay()
                headers = self.get_headers()
                
                response = self.session.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 403:
                    print(f"[!] Access forbidden. Waiting and retrying... (attempt {attempt + 1})")
                    time.sleep(random.uniform(10, 20))
                elif response.status_code == 429:
                    print(f"[!] Rate limited. Waiting longer... (attempt {attempt + 1})")
                    time.sleep(random.uniform(30, 60))
                else:
                    print(f"[!] Got status code {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"[!] Request error: {e}")
                time.sleep(5)
        
        return None

    # ==================== H&M Scraper ====================
    def scrape_hm(self, category_url, max_pages=3):
        """Scrape clothing from H&M"""
        print(f"\n[*] Scraping H&M: {category_url}")
        
        for page in range(max_pages):
            url = f"{category_url}?page={page + 1}" if page > 0 else category_url
            print(f"[*] Fetching page {page + 1}...")
            
            response = self.make_request(url)
            if not response:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find product items
            products = soup.find_all('article', class_=re.compile(r'product-item'))
            
            if not products:
                products = soup.find_all('li', class_=re.compile(r'product'))
            
            for product in products:
                try:
                    # Extract product data
                    name_elem = product.find(['h2', 'h3', 'a'], class_=re.compile(r'link|title|name'))
                    price_elem = product.find(['span', 'div'], class_=re.compile(r'price'))
                    image_elem = product.find('img')
                    link_elem = product.find('a', href=True)
                    
                    product_data = {
                        'source': 'H&M',
                        'name': name_elem.get_text(strip=True) if name_elem else 'N/A',
                        'price': price_elem.get_text(strip=True) if price_elem else 'N/A',
                        'image': image_elem.get('src') or image_elem.get('data-src') if image_elem else 'N/A',
                        'url': urljoin(url, link_elem['href']) if link_elem else 'N/A',
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    if product_data['name'] != 'N/A':
                        self.products.append(product_data)
                        print(f"  [+] Found: {product_data['name'][:50]}...")
                        
                except Exception as e:
                    continue
        
        return self.products

    # ==================== ASOS Scraper ====================
    def scrape_asos(self, category_url, max_pages=3):
        """Scrape clothing from ASOS"""
        print(f"\n[*] Scraping ASOS: {category_url}")
        
        for page in range(max_pages):
            url = f"{category_url}&page={page + 1}" if '?' in category_url else f"{category_url}?page={page + 1}"
            print(f"[*] Fetching page {page + 1}...")
            
            response = self.make_request(url)
            if not response:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find product items
            products = soup.find_all('article', {'data-auto-id': 'productTile'})
            
            if not products:
                products = soup.find_all('div', class_=re.compile(r'product'))
            
            for product in products:
                try:
                    name_elem = product.find(['h2', 'p', 'div'], class_=re.compile(r'title|name|description'))
                    price_elem = product.find(['span', 'p'], class_=re.compile(r'price'))
                    image_elem = product.find('img')
                    link_elem = product.find('a', href=True)
                    
                    product_data = {
                        'source': 'ASOS',
                        'name': name_elem.get_text(strip=True) if name_elem else 'N/A',
                        'price': price_elem.get_text(strip=True) if price_elem else 'N/A',
                        'image': image_elem.get('src') or image_elem.get('data-src') if image_elem else 'N/A',
                        'url': urljoin('https://www.asos.com', link_elem['href']) if link_elem else 'N/A',
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    if product_data['name'] != 'N/A':
                        self.products.append(product_data)
                        print(f"  [+] Found: {product_data['name'][:50]}...")
                        
                except Exception as e:
                    continue
        
        return self.products

    # ==================== Zara Scraper ====================
    def scrape_zara(self, category_url, max_pages=3):
        """Scrape clothing from Zara"""
        print(f"\n[*] Scraping Zara: {category_url}")
        
        response = self.make_request(category_url)
        if not response:
            return self.products
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Zara uses dynamic content, try to find product containers
        products = soup.find_all('li', class_=re.compile(r'product'))
        
        if not products:
            products = soup.find_all('div', class_=re.compile(r'product-grid-product'))
        
        for product in products:
            try:
                name_elem = product.find(['a', 'span', 'h2'], class_=re.compile(r'name|title|link'))
                price_elem = product.find(['span', 'div'], class_=re.compile(r'price|money'))
                image_elem = product.find('img')
                link_elem = product.find('a', href=True)
                
                product_data = {
                    'source': 'Zara',
                    'name': name_elem.get_text(strip=True) if name_elem else 'N/A',
                    'price': price_elem.get_text(strip=True) if price_elem else 'N/A',
                    'image': image_elem.get('src') or image_elem.get('data-src') if image_elem else 'N/A',
                    'url': urljoin('https://www.zara.com', link_elem['href']) if link_elem else 'N/A',
                    'scraped_at': datetime.now().isoformat()
                }
                
                if product_data['name'] != 'N/A':
                    self.products.append(product_data)
                    print(f"  [+] Found: {product_data['name'][:50]}...")
                    
            except Exception as e:
                continue
        
        return self.products

    # ==================== Generic Scraper ====================
    def scrape_generic(self, url, product_selector='article', name_selector='.product-name', 
                       price_selector='.price', image_selector='img', link_selector='a'):
        """Generic scraper for any e-commerce site"""
        print(f"\n[*] Scraping: {url}")
        
        response = self.make_request(url)
        if not response:
            return self.products
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        products = soup.select(product_selector)
        print(f"[*] Found {len(products)} product containers")
        
        for product in products:
            try:
                name_elem = product.select_one(name_selector)
                price_elem = product.select_one(price_selector)
                image_elem = product.select_one(image_selector)
                link_elem = product.select_one(link_selector)
                
                product_data = {
                    'source': urlparse(url).netloc,
                    'name': name_elem.get_text(strip=True) if name_elem else 'N/A',
                    'price': price_elem.get_text(strip=True) if price_elem else 'N/A',
                    'image': image_elem.get('src') or image_elem.get('data-src') if image_elem else 'N/A',
                    'url': urljoin(url, link_elem['href']) if link_elem and link_elem.get('href') else 'N/A',
                    'scraped_at': datetime.now().isoformat()
                }
                
                if product_data['name'] != 'N/A':
                    self.products.append(product_data)
                    print(f"  [+] Found: {product_data['name'][:50]}...")
                    
            except Exception as e:
                continue
        
        return self.products

    # ==================== Export Methods ====================
    def export_to_json(self, filename='clothes_data.json'):
        """Export scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        print(f"\n[*] Exported {len(self.products)} products to {filename}")
    
    def export_to_csv(self, filename='clothes_data.csv'):
        """Export scraped data to CSV file"""
        if not self.products:
            print("[!] No products to export")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.products[0].keys())
            writer.writeheader()
            writer.writerows(self.products)
        print(f"\n[*] Exported {len(self.products)} products to {filename}")
    
    def get_products(self):
        """Return all scraped products"""
        return self.products
    
    def clear_products(self):
        """Clear the products list"""
        self.products = []


# ==================== Selenium Version (for JavaScript-heavy sites) ====================
class SeleniumClothingScraper:
    """
    Use this class for sites that require JavaScript rendering (like Amazon, Zalando, etc.)
    Requires: pip install selenium webdriver-manager
    """
    
    def __init__(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        self.products = []
        
        # Chrome options to avoid detection
        options = Options()
        options.add_argument('--headless')  # Run in background
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # Execute script to remove webdriver flag
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def random_delay(self, min_delay=2, max_delay=5):
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def scrape_amazon_clothes(self, search_query="men clothes", max_pages=3):
        """Scrape Amazon clothing search results"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        print(f"\n[*] Scraping Amazon for: {search_query}")
        
        for page in range(1, max_pages + 1):
            url = f"https://www.amazon.com/s?k={search_query.replace(' ', '+')}&page={page}"
            print(f"[*] Fetching page {page}...")
            
            self.driver.get(url)
            self.random_delay(3, 6)
            
            # Scroll down to load lazy images
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            self.random_delay(1, 2)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.random_delay(1, 2)
            
            try:
                # Wait for products to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-component-type="s-search-result"]'))
                )
                
                products = self.driver.find_elements(By.CSS_SELECTOR, '[data-component-type="s-search-result"]')
                
                for product in products:
                    try:
                        name = product.find_element(By.CSS_SELECTOR, 'h2 a span').text
                        
                        try:
                            price = product.find_element(By.CSS_SELECTOR, '.a-price .a-offscreen').get_attribute('textContent')
                        except:
                            price = 'N/A'
                        
                        try:
                            image = product.find_element(By.CSS_SELECTOR, '.s-image').get_attribute('src')
                        except:
                            image = 'N/A'
                        
                        try:
                            link = product.find_element(By.CSS_SELECTOR, 'h2 a').get_attribute('href')
                        except:
                            link = 'N/A'
                        
                        product_data = {
                            'source': 'Amazon',
                            'name': name,
                            'price': price,
                            'image': image,
                            'url': link,
                            'scraped_at': datetime.now().isoformat()
                        }
                        
                        self.products.append(product_data)
                        print(f"  [+] Found: {name[:50]}...")
                        
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"[!] Error on page {page}: {e}")
        
        return self.products
    
    def export_to_json(self, filename='clothes_data.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        print(f"\n[*] Exported {len(self.products)} products to {filename}")
    
    def close(self):
        self.driver.quit()


# ==================== Main ====================
if __name__ == "__main__":
    print("=" * 60)
    print("  E-Commerce Clothes Scraper")
    print("=" * 60)
    
    # Choose scraping method
    print("\nSelect scraping method:")
    print("1. Basic scraper (requests + BeautifulSoup) - H&M, ASOS, Zara")
    print("2. Advanced scraper (Selenium) - Amazon, JavaScript-heavy sites")
    print("3. Custom URL scraper")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        scraper = ClothingScraper()
        
        print("\nSelect site to scrape:")
        print("1. H&M")
        print("2. ASOS")
        print("3. Zara")
        
        site = input("Enter choice: ").strip()
        
        if site == "1":
            scraper.scrape_hm("https://www2.hm.com/en_us/men/products/view-all.html", max_pages=2)
        elif site == "2":
            scraper.scrape_asos("https://www.asos.com/men/new-in/new-in-clothing/cat/?cid=6993", max_pages=2)
        elif site == "3":
            scraper.scrape_zara("https://www.zara.com/us/en/man-new-in-l1180.html", max_pages=2)
        
        if scraper.products:
            scraper.export_to_json()
            scraper.export_to_csv()
        
    elif choice == "2":
        print("\n[!] Make sure you have Chrome installed")
        print("[*] Installing required packages...")
        
        try:
            scraper = SeleniumClothingScraper()
            query = input("Enter search query (e.g., 'men shirts'): ").strip() or "men shirts"
            scraper.scrape_amazon_clothes(query, max_pages=2)
            
            if scraper.products:
                scraper.export_to_json()
            
            scraper.close()
        except ImportError:
            print("\n[!] Please install required packages:")
            print("    pip install selenium webdriver-manager")
    
    elif choice == "3":
        scraper = ClothingScraper()
        url = input("Enter URL to scrape: ").strip()
        
        print("\nEnter CSS selectors (press Enter for defaults):")
        product_sel = input("Product container selector [article]: ").strip() or "article"
        name_sel = input("Name selector [.product-name, h2, h3]: ").strip() or "h2, h3, .product-name"
        price_sel = input("Price selector [.price]: ").strip() or ".price"
        
        scraper.scrape_generic(url, product_sel, name_sel, price_sel)
        
        if scraper.products:
            scraper.export_to_json()
            scraper.export_to_csv()
    
    print("\n[*] Scraping complete!")
    if 'scraper' in dir():
        print(f"[*] Total products found: {len(scraper.products)}")
