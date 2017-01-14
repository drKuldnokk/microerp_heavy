# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

import random

def word_generator(alphabets, previous_letters=[]):
    for letter in alphabets[0]:
        letters = previous_letters + [letter]
        if len(alphabets) == 1:
            yield " ".join(letters)
        else:
            for word in word_generator(alphabets[1:], letters):
                yield word

def prepopulate_data(apps, schema_editor):
    
    # test data - products
    product_attributes = [
        ["Television", "Radio", "Washing machine", "Blender", "Phone", "Toaster", "Camera"],
        ["Sony", "Samsung", "Philips", "Bosch", "Toschiba", "Pioneer", "NEC"],
        ["X9000", "GX2000", "Z900", "XT750"],
        ["red", "yellow", "orange", "pink"],
    ]
    Product = apps.get_model("sales", "Product")
    Product.objects.all().delete()
    counts = {}
    for product_name in word_generator(product_attributes):
        id_prefix = "".join(e[0] for e in product_name.upper().split())
        if id_prefix in counts:
            counts[id_prefix] += 1
        else:
            counts[id_prefix] = 1
        num = str(counts[id_prefix])
        id = ''.join([id_prefix, "0" * (8 - len(id_prefix) - len(num)), num])
        Product.objects.create(id=id, name=product_name)

    # test data - orders
    
    # -------------------------------------------------------------------------
    # modify this number to change the number of header to be created
    # 10000 orders will create around 150000 order lines (runs around a minute)
    n_orders = 10000
    # -------------------------------------------------------------------------
    
    for n in xrange(n_orders):
        SalesOrder = apps.get_model("sales", "SalesOrder")
        SalesLine = apps.get_model("sales", "SalesLine")
        so = SalesOrder.objects.create()
        products = Product.objects.raw("""SELECT id, name
            FROM sales_product 
            WHERE id IN (
                SELECT id 
                FROM sales_product 
                ORDER BY RANDOM() 
                LIMIT %s
            )""" % random.randint(1, 30))
        for product in products:
            SalesLine.objects.create(order_id=so, product_id=product, quantity=random.randint(1, 100))

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL('''
        CREATE TABLE sales_popularity (
            product_id varchar(20) NOT NULL PRIMARY KEY REFERENCES sales_product (id),
            popularity integer
        );
        
        CREATE TRIGGER salesline_aft_insert AFTER INSERT ON sales_salesline
        BEGIN  
            INSERT OR REPLACE INTO sales_popularity (product_id, popularity)
                VALUES (
                    NEW.product_id_id,
                    (SELECT SUM(value) FROM (
                        SELECT popularity AS value FROM sales_popularity WHERE product_id = NEW.product_id_id
                        UNION ALL 
                        SELECT NEW.quantity AS value
                    ))
                );
        END;
        
        CREATE TRIGGER salesline_aft_update AFTER UPDATE ON sales_salesline
        BEGIN  
            INSERT OR REPLACE INTO sales_popularity (product_id, popularity)
                VALUES (
                    OLD.product_id_id,
                    (SELECT SUM(value) FROM (
                        SELECT popularity AS value FROM sales_popularity WHERE product_id = OLD.product_id_id
                        UNION ALL 
                        SELECT -OLD.quantity AS value
                    ))
                );
            INSERT OR REPLACE INTO sales_popularity (product_id, popularity)
                VALUES (
                    NEW.product_id_id,
                    (SELECT SUM(value) FROM (
                        SELECT popularity AS value FROM sales_popularity WHERE product_id = NEW.product_id_id
                        UNION ALL 
                        SELECT NEW.quantity AS value
                    ))
                );
        END;
        
        CREATE TRIGGER salesline_aft_delete AFTER DELETE ON sales_salesline
        BEGIN  
            INSERT OR REPLACE INTO sales_popularity (product_id, popularity)
                VALUES (
                    OLD.product_id_id,
                    (SELECT SUM(value) FROM (
                        SELECT popularity AS value FROM sales_popularity WHERE product_id = OLD.product_id_id
                        UNION ALL 
                        SELECT -OLD.quantity AS value
                    ))
                );
        END;
        '''),
        migrations.RunPython(prepopulate_data)
    ]
