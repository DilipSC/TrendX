from flask import Flask, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from twitter_scraper import scrape_twitter, store_in_mongodb
from datetime import datetime
from uuid import uuid4
import traceback
from utils import PROXY_URL

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def create_driver():
    chrome_options = Options()
    
    # Add basic Chrome options
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Configure proxy with authentication if available
    if PROXY_URL:
        try:
            from selenium.webdriver.common.proxy import Proxy, ProxyType
            
            proxy = Proxy()
            proxy.proxy_type = ProxyType.MANUAL
            
            # Extract proxy components
            proxy_parts = PROXY_URL.replace('http://', '').split('@')
            auth, host_port = proxy_parts
            username, password = auth.split(':')
            
            # Configure proxy capabilities
            proxy.http_proxy = host_port
            proxy.ssl_proxy = host_port  # Use same for HTTPS
            
            capabilities = webdriver.DesiredCapabilities.CHROME.copy()
            proxy.add_to_capabilities(capabilities)
            
            # Add proxy authentication
            chrome_options.add_argument(f'--proxy-server={host_port}')
            chrome_options.add_argument(f'--proxy-auth={username}:{password}')
            
            print("Proxy configured successfully")
            
            try:
                driver = webdriver.Chrome(
                    options=chrome_options,
                    desired_capabilities=capabilities
                )
            except TypeError:
                # For newer versions of Selenium
                driver = webdriver.Chrome(options=chrome_options)
                
        except Exception as e:
            print(f"Failed to configure proxy: {str(e)}")
            print(traceback.format_exc())
            # Try without proxy as fallback
            print("Attempting to create driver without proxy...")
            driver = webdriver.Chrome(options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)
    
    # Hide automation
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

@app.route('/scrape', methods=['POST'])
def start_scraping():
    driver = None
    try:
        # Initialize unique ID and driver
        unique_id = str(uuid4())
        print("Creating WebDriver...")
        driver = create_driver()
        print("WebDriver created successfully")
        
        try:
            # Scrape data
            print("Starting scraping...")
            trends_data = scrape_twitter(driver)
            print(f"Scraping completed. Found {len(trends_data)} trends")
            
            end_time = datetime.now()

            # Prepare MongoDB data
            data = {
                "unique_id": unique_id,
                "trends": trends_data,
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": end_time,
            }

            # Store data in MongoDB
            print("Storing data in MongoDB...")
            store_in_mongodb(data)
            print("Data stored successfully")

            return jsonify({
                "status": "success",
                "message": "Data scraped and stored successfully",
                "data": data
            }), 200

        except Exception as e:
            print(f"Error during scraping: {str(e)}")
            print(traceback.format_exc())
            return jsonify({
                "status": "error",
                "message": "Scraping failed",
                "error": str(e),
                "traceback": traceback.format_exc()
            }), 500
        finally:
            if driver:
                print("Closing WebDriver...")
                try:
                    driver.quit()
                except Exception as e:
                    print(f"Error closing driver: {str(e)}")

    except Exception as e:
        print(f"Error initializing scraper: {str(e)}")
        print(traceback.format_exc())
        if driver:
            try:
                driver.quit()
            except:
                pass
        return jsonify({
            "status": "error",
            "message": "Failed to initialize scraper",
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route('/trends', methods=['GET'])
def get_trends():
    from pymongo import MongoClient
    from utils import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME
    
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        collection = db[MONGO_COLLECTION_NAME]
        
        # Get the latest 10 trend documents
        trends = list(collection.find({})
                     .sort('timestamp', -1)
                     .limit(10))
        
        # Convert ObjectId to string for JSON serialization
        for trend in trends:
            trend['_id'] = str(trend['_id'])
            
        return jsonify({
            "status": "success",
            "data": trends
        }), 200
        
    except Exception as e:
        print(f"Error fetching trends: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to fetch trends",
            "error": str(e)
        }), 500
    finally:
        client.close()

if __name__ == '__main__':
    # Enable more detailed logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    
    print("Starting Flask server...")
    app.run(port=5000, debug=True) 