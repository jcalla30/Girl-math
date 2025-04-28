import requests
from bs4 import BeautifulSoup

def search_amazon(product_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }
    search_url = f"https://www.amazon.com/s?k={product_name.replace(' ', '+')}"
    response = requests.get(search_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the first product link (modify the selector based on Amazon's structure)
        product_link = soup.select_one("a.a-link-normal.s-no-outline")
        if product_link:
            product_url = "https://www.amazon.com" + product_link['href']
            return product_url
        else:
            return None
    else:
        return None

# Example usage
product_name = "wireless earbuds"
amazon_product_url = search_amazon(product_name)
if amazon_product_url:
    print(f"Found product URL: {amazon_product_url}")
else:
    print("Product not found on Amazon.")