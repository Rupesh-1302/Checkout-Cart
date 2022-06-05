from main import Product, Session, engine
import requests

productResponse = requests.get("https://fakestoreapi.com/products")

products = productResponse.json()

local_session = Session(bind=engine)

for product in products:
    p = Product(id=product['id'], title=product['title'], price=product['price'],
                category=product['category'], description=product['description'], image=product['image'])
    local_session.add(p)
    local_session.commit()
