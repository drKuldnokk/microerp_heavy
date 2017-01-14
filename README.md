This is a simple web app built on Django.

requirements:
    Python 2.7.12
    virtualenv 15.0.3
    Django==1.10.5
    sqlparse==0.2.2

install instructions:

    1) cd into the solution folder
    
    2) create a virtual environment
        virtualenv --no-site-packages venv
        
    3) activate virtual environment
        venv/Scripts/activate (Windows)
        . venv/bin/activate (Linux)
        
    4) install requirements (django and sqlparse)
        python -m pip install -r requirements.txt
        
    5) cd into microerp directory (there you should find manage.py)
    
    6) run migrations (this will also create test data, please see "microerp\sales\migrations\create_test_data.py")
        python manage.py migrate
        
    7) start web app at http://localhost:8000/
        python manage.py runserver
        

solution description:

    Product popularity is tracked in a separate table "sales_popularity".
    
    There are 3 triggers set on "sales_salesline" to track changes in product popularity
    
    The popularity table and triggers along with test data are created in a custom migration 
    "create_test_data.py" in microerp/sales/migrations