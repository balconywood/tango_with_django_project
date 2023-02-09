from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

def index(request):
    # Retrieve the top 5 most liked categories from database
    top_category_list = Category.objects.order_by('-likes')[:5]
    # Retrieve the top 5 most viewed pages from database
    top_page_list = Page.objects.order_by('-views')[:5]

    # Call the helper function to handle the visit counter cookies
    visitor_cookie_handler(request)

    context_dict = {
        'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!',
        'categories': top_category_list,
        'pages': top_page_list,
    }
    return render(request, 'rango/index.html', context=context_dict)

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val
def visitor_cookie_handler(request):
    # Get the number of visits to the site.
    # If the cookie is in the session data, we cast the value returned
    # to an integer.
    # If not, the default value of 1 is used.
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    # Get the last visit date/time.
    # If the cookie is in the session data, we parse the date/time string
    # to a Python datetime object, stored in the variable last_visit_time,
    # so we can use it in the comparison below.
    # If not, we use the current date and time as a default value.
    last_visit_cookie = get_server_side_cookie(request,
                                               'last_visit',
                                               str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')
    # If it's been more than a day since the last visit
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # Update the last visit cookie now we have incremented the count
        request.session['last_visit'] = str(datetime.now())
    else:
        # Set the last visit cookie
        request.session['last_visit'] = last_visit_cookie

    # Update or set the visits cookie
    request.session['visits'] = visits

def about(request):
    # Call the helper function to handle the visit counter cookies
    visitor_cookie_handler(request)

    context_dict = {
        'boldmessage': 'This tutorial has been put together by David Cannon',
        'visits': int(request.session['visits']),
    }
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

@login_required
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
            return redirect(reverse('rango:index'))
        else:
            # The supplied form contained errors - print them to the
            # terminal.
            print(form.errors)
    # Will handle the bad form, new form, or no form supplied cases.
    # Render the form with error messages, if any.
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        # Query database for category with given slug
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        # Could not find the category with the given slug
        category = None

    # You cannot add a page to a Category that does not exist...
    if category is None:
        return redirect(reverse('rango:index'))

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

def register(request):
    # A boolean flag for keeping track of if the registration was
    # successful. Initially False, set to true when we successfully
    # register the user
    registered = False

    # If we received an HTTP POST request, we're interested in
    # processing form data.
    if request.method == 'POST':
        # Attempt to get information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        # If both forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()
            # We hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now we can deal with the UserProfile instance.
            # Since we need to set the user attribute ourselves,
            # we set commit=False. This delays saving the model
            # until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # If the user provided a profile picture, we get it from
            # the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we can save the UserProfile model instance
            profile.save()

            # Update our flag to indicate the template registration
            # was successful.
            registered = True
        else:
            # Invalid form or forms - may include mistakes.
            # Print problems to the terminal.
            print(user_form.errors, profile_form.errors)
    else:
        # Not a HTTP POST request, so render our form using two
        # ModelForm instances. The forms will be blank, ready for
        # user input.
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    context_dict = {'user_form': user_form,
                    'profile_form': profile_form,
                    'registered': registered}
    return render(request, 'rango/register.html', context=context_dict)

def user_login(request):
    # If we received an HTTP POST request, try to pull out the relevant
    # information
    if request.method == 'POST':
        # Get the username and password provided by the user. This
        # information is obtained from the login form. We use
        # request.POST.get('<variable>') instead of
        # request.POST['<variable>'] since the former returns None
        # if the value does not exist, while the latter raises a
        # KeyError exception.
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/
        # password combination is valid - a User object is returned if
        # it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absense of a value),
        # no user with matching credentials was found.
        if user:
            # Check the account is active and is not disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user
                # in. We'll send the user back to the homepage.
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                # An inactive account was used - we won't log the user in.
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided, so we can't log the user in.
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    # The request is not an HTTP POST, so display the login form.
    # This scenario would most likely be an HTTP GET.
    else:
        # No context variables to pass to the tamplate system here,
        # hence the blank dictionary object
        return render(request, 'rango/login.html')

# Use the login_required() decorator to ensure only those logged in can
# access the view.
@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

# Use the login_required() decorator to ensure only those logged in can
# access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Redirect the user back to the homepage.
    return redirect(reverse('rango:index'))
