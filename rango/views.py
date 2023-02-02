from django.shortcuts import render, redirect
from django.urls import reverse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm

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

def add_category(request):
    form = CategoryForm()

    # If we received an HTTP POST request - the user submitted data
    # via the form
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # If we've been provided with a valid form
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now the category is saved, redirect the user back to the
            # index view.
            return redirect('/rango/')
        else:
            # The supplied form contained errors - print them to the
            # terminal.
            print(form.errors)
    # Will handle the bad form, new form, or no form supplied cases.
    # Render the form with error messages, if any.
    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
    try:
        # Query database for category with given slug
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        # Could not find the category with the given slug
        category = None

    # You cannot add a page to a Category that does not exist...
    if category is None:
        return redirect('/rango/')

    form = PageForm()

    # If we received an HTTP POST request - the user submitted data
    # via the form
    if request.method == 'POST':
        form = PageForm(request.POST)

        # If we've been provided with a valid form
        if form.is_valid():
            if category:
                # Save the new page to the database
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                # Now the page is saved, redirect the user back to the
                # category view.
                return redirect(reverse('rango:show_category',
                                        kwargs={'category_name_slug':
                                                category_name_slug}))
        else:
            # The supplied form contained errors - print them to the
            # terminal.
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)
