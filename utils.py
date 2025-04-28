import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import numpy as np

def extract_asin(amazon_url):
    """Extract ASIN from Amazon product URL"""
    # Pattern for ASIN in Amazon URLs
    patterns = [
        r'/dp/(\w{10})',
        r'/gp/product/(\w{10})',
        r'/ASIN/(\w{10})',
        r'amazon\.com.*?/(\w{10})(?:/|\?|$)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, amazon_url)
        if match:
            return match.group(1)
    
    return None

def get_amazon_product_info(api, asin):
    """Get Amazon product information using Keepa API"""
    try:
        # Query the Keepa API
        products = api.query(asin, domain='US')
        if not products:
            return None
        
        product = products[0]
        
        # Extract the product title
        title = product.get('title', 'Unknown Product')
        
        # Extract price history
        price_data = product['data']['NEW']
        
        # Convert Keepa's price format (in cents) to dollars
        valid_prices = [p/100 for p in price_data if p and p > 0]
        
        if not valid_prices:
            return None
        
        current_price = valid_prices[-1]
        peak_price = max(valid_prices)
        lowest_price = min(valid_prices)
        
        return {
            'title': title,
            'price_data': valid_prices,
            'current_price': current_price,
            'peak_price': peak_price,
            'lowest_price': lowest_price,
            'asin': asin
        }
    
    except Exception as e:
        print(f"Error getting Amazon product info: {str(e)}")
        return None

def search_walmart(item_title):
    """Search Walmart for a product and return the price"""
    try:
        # Limit the query to the first few words to improve search results
        words = item_title.split()
        query = ' '.join(words[:6])
        
        # Format search query
        query = query.replace(' ', '+')
        url = f"https://www.walmart.com/search?q={query}"
        
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.walmart.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Send request
        response = requests.get(url, headers=headers, timeout=10)
        
        # Check if request was successful
        if response.status_code != 200:
            return None
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Different possible selectors for Walmart prices
        price_selectors = [
            'span[data-automation-id="product-price"]',
            'span.price-characteristic',
            'span.price-group',
            'div.product-price-container span.price'
        ]
        
        # Try each selector
        for selector in price_selectors:
            prices = soup.select(selector)
            if prices and len(prices) > 0:
                return prices[0].text.strip()
        
        return None
    
    except Exception as e:
        print(f"Error searching Walmart: {str(e)}")
        return None

def girl_math_logic(current_price, peak_price, lowest_price):
    """Apply Girl Math logic to calculate savings"""
    savings_from_peak = peak_price - current_price
    if peak_price > 0:  # Avoid division by zero
        savings_percentage = (savings_from_peak / peak_price) * 100
    else:
        savings_percentage = 0
    
    # Girl Math always makes it look like a better deal!
    # The higher the difference between peak and current, the better the deal
    enhanced_savings = savings_from_peak * 1.1  # Enhance savings by 10% (Girl Math magic!)
    enhanced_percentage = savings_percentage * 1.05  # Enhance percentage by 5%
    
    return enhanced_savings, enhanced_percentage
