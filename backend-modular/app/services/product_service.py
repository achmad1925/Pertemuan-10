class ProductService:
    def __init__(self, repo):
        self.repo = repo

    def fetch_products(self):
        return self.repo.get_all()

    def fetch_product_details(self, product_id):
        product = self.repo.get_by_id(product_id)
        if not product:
            return {"error": "Produk tidak ditemukan"}, 404
        return {"status": "succes", "data": product},200

    def add_new_product(self, data):
        if not data or "name" not in data or "price" not in data:
            return {"error": "Nama dan harga wajib diisi"}, 400
        if data["price"] <= 0:
            return {"error": "harga harus lebih besar dari 0"}, 400
        created = self.repo.create(data["name"], data["price"])
        return {"status": "succes", "data": created}, 201