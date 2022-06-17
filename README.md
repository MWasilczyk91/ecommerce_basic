# e-commerce basic


Simple e-commerce shopping application

## About

This is a simple django shopping application. It enables adding products to shelves,
shelves to carts and making orders out of carts. The main feature of the app is
to enforce daily limits on orders which vary depending on the region provided.
The global limit always takes precedence over regional limits.

## Installation and running

Create and run virtual env:
```
python3 -m venv env
source env/bin/activate
```

Install requirements:
```
pip3 install -r requirements.txt
```

Prepare the database (the app uses sqlite) and create an admin user:
```
python manage.py migrate
python manage.py createsuperuser --email admin@example.com --username admin
```

Add the required task schedule to DjangoQ:
```
python manage.py add_reset_limits_schedule
```

Run the qcluster process to be able to execute periodically scheduled tasks:
```
python manage.py qcluster
```

Finally, run the app:
```
python manage.py runserver
```

## Unit tests

To run all unit tests use:
```
python manage.py test
```

To run a specific unit test function:
```
python manage.py test <module>.<test_case>.<test_function>
```
Example:
```
python manage.py test shopping.tests.MakeOrderTestCase.test_make_order_accepted
```