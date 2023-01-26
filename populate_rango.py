import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')

import django
django.setup()
from rango.models import Category, Page

def populate():
    python_pages = [
        {
            'title': 'Official Python Tutorial',
            'url': 'http://docs.python.org/3/tutorial/',
            'views': 65,
        },
        {
            'title' : 'How to Think like a Computer Scientist',
            'url': 'http://www.greenteapress.com/thinkpython/',
            'views': 77,
        },
        {
            'title': 'Learn Python in 10 Minutes',
            'url': 'http://www.korokithakis.net/tutorials/python/',
            'views': 16,
        },
    ]
    django_pages = [
        {
            'title': 'Official Django Tutorial',
            'url': 'https://docs.djangoproject.com/en/2.1/intro/tutorial01/',
            'views': 22,
        },
        {
            'title': 'Django Rocks',
            'url': 'http://www.djangorocks.com/',
            'views': 97,
        },
        {
            'title': 'How to Tango with Django',
            'url': 'http://www.tangowithdjango.com/',
            'views': 46,
        },
    ]
    other_pages = [
        {
            'title': 'Bottle',
            'url': 'http://bottlepy.org/docs/dev',
            'views': 60,
        },
        {
            'title': 'Flask',
            'url': 'http://flask.pocoo.org',
            'views': 53,
        },
    ]

    categories = {
        'Python': {
            'pages': python_pages,
            'views': 128,
            'likes': 64,
        },
        'Django': {
            'pages': django_pages,
            'views': 64,
            'likes': 32,
        },
        'Other Frameworks': {
            'pages': other_pages,
            'views': 32,
            'likes': 16,
        }
    }

    # For each category in our dictionary above
    for category, category_data in categories.items():
        # Add the category to the database
        db_category = add_category(category, category_data['views'], category_data['likes'])
        for page in category_data['pages']:
            # Add each of the category's associated pages to the databasd
            add_page(db_category, page['title'], page['url'], page['views'])

    # Print each category and its associated pages that we've added
    # to the database
    for db_category in Category.objects.all():
        for db_page in Page.objects.filter(category=db_category):
            print(f'- {db_category}: {db_page}')

def add_page(category, title, url, views=0):
    # Add page to database, returning a reference to the page model
    # instance if it already exists. The get_or_create method returns
    # a tuple with a reference to the model instance, and a boolean
    # indicating if the model instance had to be created (false if
    # already existed), so we get the object reference from index 0
    db_page = Page.objects.get_or_create(category=category, title=title, url=url, views=views)[0]
    db_page.save()
    return db_page

def add_category(name, views, likes):
    # Add category to database, returning a reference to the category
    # model instance if it already exists. The get_or_create method
    # returns a tuple with a reference to the model instance, and a
    # boolean indicating if the model instance had to be created (false
    # if already existed), so we get the object reference from index 0
    db_category = Category.objects.get_or_create(name=name, views=views, likes=likes)[0]
    db_category.save()
    return db_category

# Execution starts from here
if __name__ == '__main__':
    print('Starting Rango population script...')
    populate()