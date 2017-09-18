This is a repository for curating the Lakeland Omeka site.

    http://lakeland.umd.edu

Get the Lakeland Data

    aws s3 sync s3://mith-bags/A36E23C8-45E3-4ECD-8D8E-610CEDF60441/data data

Install some things (Ubuntu):

    sudo apt-get install mysql-server libmysqlclient-dev python3-pip
    pip install pipenv
    pipenv install

Populate the database:

    zcat data/omkealakeland.sql.gz | mysql -u root omkealakeland.sql.gz

Set these in your environment:

    export DB_NAME=omekadblakeland
    export DB_USER=root
    export DB_PASSWORD=changeme

Now you can interact with the database from python, for example:

    ./oralhistories.py
