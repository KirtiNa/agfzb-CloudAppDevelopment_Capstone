from email import message
from wsgiref.validate import validator
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from simplejson import JSONDecodeError
# from .models import related models
from .restapis import get_request,get_dealers_from_cf,get_dealer_by_id_from_cf,post_request,get_dealer_reviews_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from django.urls import reverse
from .models import CarModel,DealerReview
# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
# def about(request):
# ...
def about(request):
    return render(request, 'djangoapp/about.html')

# Create a `contact` view to return a static contact page
#def contact(request):
def contact(request):
    return render(request, 'djangoapp/contact.html')
# Create a `login_request` view to handle sign in request
# def login_request(request):
# ...
def login_request(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(to=reverse('admin:index'))
        else:
            return redirect('djangoapp:index')

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
# def registration_request(request):
# ...

def registration_request(request):
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url="https://us-south.functions.appdomain.cloud/api/v1/web/kinawal1%40in.ibm.com_myspaceapp/dealership-package/get-dealerships"
        dealerships=get_dealers_from_cf(url)
        context["dealership_list"] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...

def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context = {}
        dealer_url = "https://us-south.functions.appdomain.cloud/api/v1/web/kinawal1%40in.ibm.com_myspaceapp/dealership-package/get-dealerships"
        dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id=dealer_id)
        context["dealer"] = dealer
        
        review_url = "https://us-south.functions.appdomain.cloud/api/v1/web/kinawal1%40in.ibm.com_myspaceapp/dealership-package/get-reviews"
        reviews = get_dealer_reviews_from_cf(review_url, dealer_id=dealer_id)
        context["reviews"] = reviews
        print(dealer_id)
    return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request,dealer_id):
    context = {}
    if request.method == 'GET':
        dealer_url = "https://us-south.functions.appdomain.cloud/api/v1/web/kinawal1%40in.ibm.com_myspaceapp/dealership-package/get-dealerships"
        dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id=dealer_id)
        context["dealer"] = dealer
  
        # Get cars for the dealer
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        context["cars"] = cars
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == 'POST':
        if request.user.is_authenticated:
            username = request.user.username
            print(request.POST)
            payload = dict()
            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)
            print("car id",car)
           
            payload["time"] = datetime.utcnow().isoformat()
            payload["name"] = request.POST['name']
            payload["dealership"] = dealer_id
            payload["review"] = request.POST["content"]
            payload["purchase"] = False
            if "purchasecheck" in request.POST:
                if request.POST["purchasecheck"] == 'on':
                    payload["purchase"] = True
            payload["purchase_date"] = request.POST["purchasedate"]
            payload["car_make"] = car.make.name
            payload["car_model"] = car.name
            payload["car_year"] = int(car.year.strftime("%Y"))

            new_payload = {}
            new_payload["review"] = payload

            
            # print("new_payload", new_payload)
            review_post_url = "https://us-south.functions.appdomain.cloud/api/v1/web/kinawal1%40in.ibm.com_myspaceapp/dealership-package/create-reviews"
            try:
              post_request(review_post_url, new_payload, dealer_id=dealer_id)
            except ValueError:
               print("hello")
            
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        

    
