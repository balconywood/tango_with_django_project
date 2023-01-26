from django.shortcuts import render
from rango.models import Category, Page

def index(request):
    # Retrieve the top 5 most liked categories from database
    top_category_list = Category.objects.order_by('-likes')[:5]
    # Retrieve the top 5 most viewed pages from database
    top_page_list = Page.objects.order_by('-views')[:5]

    context_dict = {
        'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!',
        'categories': top_category_list,
        'pages': top_page_list,
    }
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage matches to {{ boldmessage }} in the template!
    context_dict = {'boldmessage': 'This tutorial has been put together by David Cannon'}

    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render(request, 'rango/about.html', context=context_dict)

def show_category(request, category_name_slug):
    context_dict = {}

    try:
        # Query database for category with given slug
        category = Category.objects.get(slug=category_name_slug)
        # Retrieve all of the associated pages
        pages = Page.objects.filter(category=category)

        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        # Could not find the category with the given slug
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context=context_dict)
