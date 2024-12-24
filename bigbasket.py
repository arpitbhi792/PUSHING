import requests
import json
import pandas as pd

# Create a session and set the headers and cookies
session = requests.Session()

headers = {
    "Sec-Ch-Ua": "\"-Not.A/Brand\";v=\"8\", \"Chromium\";v=\"102\"",
    "Accept": "*/*",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
    "Referer": "https://www.bigbasket.com/ps/?q=rice&nc=as&page=3&filter=%5B%5D&sortBy=%7B%22display_name%22%3A%22%25+Off+-+High+to+Low%22%2C%22value%22%3A%22dphtl%22%2C%22is_selected%22%3Afalse%7D",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Dest": "empty",
    "Accept-Encoding": "gzip, deflate",
    "Sec-Fetch-Mode": "cors",
    "X-Channel": "BB-WEB",
    "X-Tracker": "de5e28cf-8ed0-4470-9a43-2989b199913b",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua-Mobile": "?0",
    "Content-Type": "application/json"
}
cookies = {
    "BBAUTHTOKEN": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjaGFmZiI6IjhXeFZ0TUl1MDhvWURnIiwidGltZSI6MTczNDc5MzM5Mi4wNzMzNzE2LCJtaWQiOjQ2NzQyMTQwLCJ2aWQiOjUxNTQ1Mjg2NTc4ODk5Nzg4OCwiZGV2aWNlX2lkIjoiV0VCIiwic291cmNlX2lkIjoxLCJlY19saXN0IjpbMyw0LDEwLDEyLDEzLDE0LDE1LDE2LDE3LDIwLDEwMF0sIlRETFRPS0VOIjoiOTU1MjRlZmEtMjE2MC00ZTAxLTkyNzQtOTRjZTVkMmJmNTgyIiwicmVmcmVzaF90b2tlbiI6IjE1ZDgzMzFiLTAyNDctNGExZi1hNzEyLWY1MTFhODY2ZjlhNCIsInRkbF9leHBpcnkiOjE3MzUzOTgxOTEsImV4cCI6MTc1MDU3MzM5MiwiaXNfc2FlIjpudWxsLCJkZXZpY2VfbW9kZWwiOiJXRUIiLCJkZXZpY2VfaXNfZGVidWciOiJmYWxzZSJ9.x5Yt0oRGCgboFXOsp32feX9Ll0dJ5IfQCcnw7tj-1i0"
}

# Initialize an empty list to store all products' data
all_product_data = []

# Function to process each page
def process_page(page_num, product_slug):
    paramsGet = {"page": str(page_num), "sort": "dphtl", "type": "ps", "slug": product_slug}
    response = session.get("https://www.bigbasket.com/listing-svc/v2/products", params=paramsGet, headers=headers, cookies=cookies)
    
    if response.status_code == 200:
        try:
            data = response.json()

            # Initialize a list to hold product data for the current page
            product_data = []

            def extract_data_from_response(data):
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key == 'absolute_url' and isinstance(value, str):
                            product_info = {
                                "Product Name (Slug)": product_slug,
                                "Absolute URL": value,
                                "MRP": "N/A",
                                "Discount Text": "N/A",
                                "Selling Price": "N/A"
                            }

                            # Try to get pricing data (mrp, d_text, sp) if available
                            if 'pricing' in data:
                                pricing = data['pricing'].get('discount', {})
                                product_info["MRP"] = pricing.get('mrp', 'N/A')
                                product_info["Discount Text"] = pricing.get('d_text', 'N/A')
                                product_info["Selling Price"] = pricing.get('prim_price', {}).get('sp', 'N/A')

                            # Only append if the discount percentage is greater than 70%
                            discount_text = product_info["Discount Text"]
                            if discount_text is not None and "OFF" in discount_text:
                                try:
                                    discount_percentage = float(discount_text.split('%')[0])
                                    if discount_percentage > 70:
                                        product_data.append(product_info)

                                        # Log details to the console
                                        print(f"Product: {product_slug} - Page {page_num} - Found product with >70% discount: {product_info}")
                                except ValueError:
                                    pass

                        # Recurse into nested structures (lists or dicts)
                        elif isinstance(value, (dict, list)):
                            extract_data_from_response(value)

                elif isinstance(data, list):
                    for item in data:
                        extract_data_from_response(item)

            # Start extracting data from the current page
            extract_data_from_response(data)

            # Add the product data of the current page to the overall list
            all_product_data.extend(product_data)

        except json.JSONDecodeError:
            print(f"Failed to decode the response as JSON on page {page_num}.")
    else:
        print(f"Request failed with status code: {response.status_code} on page {page_num}.")

# List of product slugs (names)
product_slugs = ['rice', 'sugar', 'flour', 'pulses']  # Add the product names you want to search for

# Loop through each product slug
for product_slug in product_slugs:
    print(f"Starting search for '{product_slug}'...")

    # Loop through the first 20 pages for each product
    for page_num in range(1, 21):
        process_page(page_num, product_slug)

# Convert the list of product data into a DataFrame and save it to an Excel file
if all_product_data:
    df = pd.DataFrame(all_product_data)
    df.to_excel('filtered_product_data_all_products_with_slug.xlsx', index=False)
    print("Data extraction complete. Products with >70% discount from all pages for all products have been saved to 'filtered_product_data_all_products_with_slug.xlsx'.")
else:
    print("No products with >70% discount found in the first 20 pages.")
