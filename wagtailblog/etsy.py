import requests

response = requests.get('https://openapi.etsy.com/v2/shops/21292598/listings/active?includes=Images:1:0&api_key=7mnagooquhyc2hise129xdlo')
etsy_data = response.json()