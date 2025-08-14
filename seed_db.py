from crm.models import Customer, Product

def seed():
    # Seed customers
    Customer.objects.get_or_create(name="Alice", email="alice@example.com", phone="+1234567890")
    Customer.objects.get_or_create(name="Bob", email="bob@example.com", phone="123-456-7890")
    Customer.objects.get_or_create(name="Carol", email="carol@example.com")
    # Seed products
    Product.objects.get_or_create(name="Laptop", price=999.99, stock=10)
    Product.objects.get_or_create(name="Phone", price=499.99, stock=20)
    print("Seeded initial data.")

if __name__ == "__main__":
    seed()
