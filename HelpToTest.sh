# Once you have all the translations set, you must compile them with
python manage.py compilemessages -l ru

# run functional tests
python manage.py test functional_tests

# run unittests
python manage.py test taskbuster.test

# run both the unittests and functional tests together
python manage.py test

# run tests with coverage using
coverage run --source='.' manage.py test
coverage report
coverage html # you can see the results in htmlcov/index.html