import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ProductService:
    @staticmethod
    def get_product(product_id):
        try:
            response = requests.get(f"{settings.PRODUCT_SERVICE_URL}{product_id}/")
            print(response)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching product {product_id}: {e}")
            return None
    
    @staticmethod
    def check_product_availability(product_id, quantity):
        product = ProductService.get_product(product_id)
        if not product:
            return False
        return product['stock'] >= quantity
    
    @staticmethod
    def update_product_stock(product_id, quantity):
        product = ProductService.get_product(product_id)
        if not product:
            return False
        
        new_stock = product['stock'] - quantity
        if new_stock < 0:
            return False
        
        try:
            response = requests.put(
                f"{settings.PRODUCT_SERVICE_URL}{product_id}/",
                json={"stock": new_stock, "name": product['name'], 
                      "description": product['description'], "price": product['price']}
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating product {product_id}: {e}")
            return False