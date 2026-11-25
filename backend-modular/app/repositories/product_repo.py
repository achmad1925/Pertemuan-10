class ProductRepository:
    def __init__(self):        
        self.products = [            
            {"id": 1, "name": "Laptop Pro", "price": 15000000},            
            {"id": 2, "name": "Mechanical Keyboard", "price": 850000}
            ]    

    def get_all(self):        
        return self.products    
        
    def get_by_id(self, product_id):
        return next((p for p in self.products if p["id"] == product_id), None)
      
    def create(self, name, price):
        product = {"id": len(self.products) + 1, "name": name, "price": price}
        self.products.append(product)
        return product