from __future__ import unicode_literals

from django.db import models

class Product(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=500)
    
class SalesOrder(models.Model):
    pass

class SalesLine(models.Model):
    order_id = models.ForeignKey(SalesOrder)
    product_id = models.ForeignKey(Product)
    quantity = models.IntegerField()