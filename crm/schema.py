import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
import re

# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount")

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def validate_phone(phone):
        if not phone:
            return True
        pattern = r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$"
        return re.match(pattern, phone)

    @classmethod
    def mutate(cls, root, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            return cls(customer=None, message="Email already exists")
        if phone and not cls.validate_phone(phone):
            return cls(customer=None, message="Invalid phone format")
        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return cls(customer=customer, message="Customer created successfully")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(graphene.JSONString, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        created = []
        errors = []
        with transaction.atomic():
            for idx, data in enumerate(input):
                name = data.get("name")
                email = data.get("email")
                phone = data.get("phone")
                if not name or not email:
                    errors.append(f"Row {idx+1}: Name and email required")
                    continue
                if Customer.objects.filter(email=email).exists():
                    errors.append(f"Row {idx+1}: Email already exists")
                    continue
                if phone and not CreateCustomer.validate_phone(phone):
                    errors.append(f"Row {idx+1}: Invalid phone format")
                    continue
                customer = Customer(name=name, email=email, phone=phone)
                customer.save()
                created.append(customer)
        return cls(customers=created, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        stock = graphene.Int()

    product = graphene.Field(ProductType)

    @classmethod
    def mutate(cls, root, info, name, price, stock=0):
        if price <= 0:
            raise ValidationError("Price must be positive")
        if stock is not None and stock < 0:
            raise ValidationError("Stock cannot be negative")
        product = Product(name=name, price=price, stock=stock or 0)
        product.save()
        return cls(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime()

    order = graphene.Field(OrderType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return cls(order=None, message="Invalid customer ID")
        products = Product.objects.filter(pk__in=product_ids)
        if products.count() != len(product_ids):
            return cls(order=None, message="One or more product IDs are invalid")
        if not products:
            return cls(order=None, message="At least one product must be selected")
        order = Order(customer=customer, order_date=order_date or timezone.now())
        order.save()
        order.products.set(products)
        total = sum([p.price for p in products])
        order.total_amount = total
        order.save()
        return cls(order=order, message="Order created successfully")

# Query class
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(root, info):
        return Customer.objects.all()
    def resolve_products(root, info):
        return Product.objects.all()
    def resolve_orders(root, info):
        return Order.objects.all()

# Mutation class
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
