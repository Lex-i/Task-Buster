# You can deactivate the virtual environment with
deactivate

# and activate it again with
workon tb_dev
workon tb_test

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

# start the Postgres command line utility
psql -h localhost
sudo -u postgres psql
sudo -u postgres psql taskbuster_db

\q # exit this environment
\? # for more help, 
\list # to list your databases
\du # to list your users
\d # to list your tablenames
\d tablename # to show full info about table incl. constraits, key and etc.

# Go back to the root folder, which contains the manage.py file and run next c:
python manage.py check
python manage.py makemigrations taskmanager
python manage.py migrate taskmanager

# should create another Client/secret pair for production, 
# and change http://127.0.0.1:8000/ by your website domain

# Don’t forget to commit your changes:
git add .
git status
git commit -m "Something's done"
git push origin master