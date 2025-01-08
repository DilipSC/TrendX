from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from uuid import uuid4
from pymongo import MongoClient
from datetime import datetime
from utils import (
    TWITTER_USERNAME, 
    TWITTER_PASSWORD, 
    PROXY_URL, 
    MONGO_URI, 
    MONGO_DB_NAME, 
    MONGO_COLLECTION_NAME
)
import sys

# Configure ProxyMesh in Selenium
def configure_driver():
    chrome_options = Options()
    
    # Set up proxy with authentication
    if PROXY_URL:
        # Extract proxy components
        proxy_parts = PROXY_URL.replace('http://', '').split('@')
        auth = proxy_parts[0]
        host_port = proxy_parts[1]
        
        # Configure proxy with authentication
        chrome_options.add_argument(f'--proxy-server=http://{host_port}')
        
        # Add proxy authentication extension
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                  singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                  },
                  bypassList: ["localhost"]
                }
              };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (
            host_port.split(':')[0],  # host
            host_port.split(':')[1],  # port
            auth.split(':')[0],       # username
            auth.split(':')[1]        # password
        )
        
        import os
        import tempfile
        import zipfile
        
        # Create a temporary directory for the extension
        temp_dir = tempfile.mkdtemp()
        
        # Create manifest.json
        manifest_file = os.path.join(temp_dir, 'manifest.json')
        with open(manifest_file, 'w') as f:
            f.write(manifest_json)
            
        # Create background.js
        background_file = os.path.join(temp_dir, 'background.js')
        with open(background_file, 'w') as f:
            f.write(background_js)
            
        # Zip the extension
        zip_path = os.path.join(tempfile.gettempdir(), 'proxy_auth_extension.zip')
        with zipfile.ZipFile(zip_path, 'w') as zp:
            zp.write(manifest_file, 'manifest.json')
            zp.write(background_file, 'background.js')
            
        chrome_options.add_extension(zip_path)
    
    # Add other options to avoid detection
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Create and return the driver
    driver = webdriver.Chrome(service=Service(), options=chrome_options)
    
    # Update navigator.webdriver flag to prevent detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

# Scrape Twitter "What's Happening" section
def scrape_twitter(driver):
    try:
        # Navigate to Twitter login
        driver.get("https://x.com/login")
        
        # Wait for and enter username
        username_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        username_field.clear()
        username_field.send_keys(TWITTER_USERNAME)
        username_field.send_keys(Keys.RETURN)
        
        # Wait for and enter password
        password_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_field.clear()
        password_field.send_keys(TWITTER_PASSWORD)
        password_field.send_keys(Keys.RETURN)

        # Wait for "What's Happening" section
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Timeline: Trending now']"))
        )
        
        # Get all trending topics with their details
        trending_items = driver.find_elements(
            By.XPATH, 
            "//div[@aria-label='Timeline: Trending now']/div/div"
        )

        trends_data = []
        for item in trending_items:
            try:
                trend_info = {}
                
                # Get category (if exists)
                categories = item.find_elements(By.XPATH, ".//span[contains(text(), '·')]/preceding-sibling::span")
                if categories:
                    trend_info['category'] = categories[0].text
                
                # Get trend name/headline
                headlines = item.find_elements(By.XPATH, ".//span[contains(@class, 'css-')]")
                if headlines:
                    trend_info['headline'] = headlines[0].text
                
                # Get tweet count or description
                tweet_counts = item.find_elements(By.XPATH, ".//span[contains(text(), 'posts') or contains(text(), 'K') or contains(text(), 'M')]")
                if tweet_counts:
                    trend_info['tweet_count'] = tweet_counts[0].text
                
                # Get description if available
                descriptions = item.find_elements(By.XPATH, ".//div[contains(@class, 'css-')]/span")
                if descriptions and len(descriptions) > 1:
                    trend_info['description'] = descriptions[1].text
                
                if trend_info:  # Only append if we found some information
                    trends_data.append(trend_info)
                
            except Exception as e:
                print(f"Error processing trend item: {str(e)}")
                continue

        if not trends_data:
            print("Warning: No trending topics found")
            return []

        return trends_data
        
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        raise

# Store results in MongoDB
def store_in_mongodb(data):
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]
    
    # Add timestamp and metadata
    data['timestamp'] = datetime.now()
    data['source'] = 'twitter_whats_happening'
    
    collection.insert_one(data)

if __name__ == "__main__":
    try:
        unique_id = str(uuid4())
        driver = configure_driver()

        try:
            # Scrape data
            trends_data = scrape_twitter(driver)
            ip_address = PROXY_URL.split("@")[-1].split(":")[0] if PROXY_URL else 'local'
            end_time = datetime.now()

            # Prepare MongoDB data
            data = {
                "unique_id": unique_id,
                "trends": trends_data,
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "ip_address": ip_address,
            }

            # Store data in MongoDB
            store_in_mongodb(data)
            print("Data stored successfully!")
            print("\nTrending Topics:")
            for trend in trends_data:
                print("\n---")
                for key, value in trend.items():
                    print(f"{key}: {value}")
                
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"Error during execution: {str(e)}", file=sys.stderr)
        sys.exit(1)
