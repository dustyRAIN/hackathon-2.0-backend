import uuid

from django.db import models


class ModelWithTimeStamp():
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Author(models.Model, ModelWithTimeStamp):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    unique_id = models.CharField(max_length=1024, unique=True, default=uuid.uuid4)
    url = models.CharField(max_length=1024, blank=True, null=False)
    title = models.CharField(max_length=1024, blank=True, null=False)
    big_metadata = models.JSONField(blank=True, null=True)
    secret_value = models.JSONField(blank=True, null=True)
    followers = models.IntegerField(default=0)


class Tag(models.Model, ModelWithTimeStamp):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)


class Content(models.Model, ModelWithTimeStamp):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    unique_id = models.CharField(max_length=1024, unique=True, default=uuid.uuid4)
    url = models.CharField(max_length=1024, blank=True, )
    title = models.TextField(blank=True)
    like_count = models.BigIntegerField(blank=True, null=False, default=0, )
    comment_count = models.BigIntegerField(blank=True, null=False, default=0, )
    view_count = models.BigIntegerField(blank=True, null=False, default=0, )
    share_count = models.BigIntegerField(blank=True, null=False, default=0, )
    thumbnail_url = models.URLField(max_length=1024, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True, )
    big_metadata = models.JSONField(blank=True, null=True)
    secret_value = models.JSONField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, through='ContentTag')


class ContentTag(models.Model, ModelWithTimeStamp):
    """
    TODO: The content and tag is being duplicated, need to do something in the database
    """
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

class Address(models.Model, ModelWithTimeStamp):
    address_id = models.AutoField(primary_key=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    name = models.CharField(max_length=300)


class Supplier(models.Model, ModelWithTimeStamp):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=255)
    supplier_contact_name = models.CharField(max_length=255)
    supplier_email = models.EmailField()
    supplier_phone = models.CharField(max_length=20)


class Inventory(models.Model, ModelWithTimeStamp):
    warehouse_id = models.AutoField(primary_key=True)
    warehouse_name = models.CharField(max_length=255)
    warehouse_location = models.ForeignKey(Address, null=True, on_delete=models.SET_NULL)
    shelf_number = models.CharField(max_length=50)
    reorder_point = models.IntegerField()
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)


class Payment(models.Model, ModelWithTimeStamp):
    payment_id = models.AutoField(primary_key=True)
    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)


class Product(models.Model, ModelWithTimeStamp):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    product_description = models.TextField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    # TODO: may sepratare out category if time permits
    product_category = models.CharField(max_length=100)
    product_subcategory = models.CharField(max_length=100)
    product_brand = models.CharField(max_length=100)
    product_stock = models.IntegerField()
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    @property
    def product_ratings(self):
        return self.review_set.all()


class UserInfo(models.Model, ModelWithTimeStamp):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)  # Storing password hashes in the same table is a security risk
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=20)
    is_admin = models.BooleanField(default=False)
    address = models.ForeignKey(Address, null=True, on_delete=models.SET_NULL)
    wishlist = models.ManyToManyField(Product)


class Review(models.Model, ModelWithTimeStamp):
    reviewer = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    review_text = models.TextField(null=True, blank=True)
    review_rating = models.IntegerField(null=True, blank=True)
    review_date = models.DateTimeField(null=True, blank=True)


class MarketingCampaign(models.Model, ModelWithTimeStamp):
    campaign_id = models.AutoField(primary_key=True)
    campaign_name = models.CharField(max_length=255, null=True, blank=True)
    discount_code = models.CharField(max_length=50, null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)


class Order(models.Model, ModelWithTimeStamp):
    order_id = models.AutoField(primary_key=True)
    order_date = models.DateTimeField()
    order_status = models.CharField(max_length=50)
    shipping_method = models.CharField(max_length=100)
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    payment = models.ForeignKey(Payment, null=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItemInfo')


class OrderItemInfo(models.Model, ModelWithTimeStamp):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    marketing_campaign = models.ForeignKey(MarketingCampaign, null=True, on_delete=models.SET_NULL)


class CustomerServiceTicket(models.Model, ModelWithTimeStamp):
    support_ticket_id = models.AutoField(primary_key=True)
    support_ticket_status = models.CharField(max_length=50, null=True, blank=True)
    support_agent_name = models.CharField(max_length=255, null=True, blank=True)
    customer = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
