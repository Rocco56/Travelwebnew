from django.shortcuts import render, redirect
from .models import *
import pandas as pd
import pickle
import os
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import googlemaps
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.urls import reverse
# Create your views here.

def index(request):
    user = request.user
    places = PlaceMode.objects.all()
    return render(request, 'bharat-site.html', {"places" : places[0: 3], 'user': user})

def details(request, pk):
    place = PlaceMode.objects.get(id=pk)
    places_pickle = os.path.join(settings.MEDIA_ROOT, 'places.pkl')
    similarity_pickle = os.path.join(settings.MEDIA_ROOT, 'similarity.pkl')
        
    place_dict = pickle.load(open(places_pickle, 'rb'))
    similarity = pickle.load(open(similarity_pickle, 'rb'))
    name = place.Name
    place_index = place_dict[place_dict['Name'] == name].index[0]
    distances = similarity[place_index]
    places_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x : x[1])[1:5]
    recommended_places = []
    for i in places_list:
        recommended_places.append(PlaceMode.objects.get(id=i[0]))
    crowd_data = CrowdModel.objects.filter(location=place)
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'Augast', 'September', 'October', 'November', 'December']
    data = []
    reviews = TripReview.objects.filter(place=place)
    print(reviews)
    return render(request, 'place-details.html', {"rec_places" : recommended_places, 'single_place' : place, 'crowd_data' : crowd_data, 'months': months, 'reviews':reviews})

def search_view(request):
    query = request.GET.get('q', '')
    state = request.GET.get('state', '')
    place_type = request.GET.get('type', '')

    results = PlaceMode.objects.all()
    print(query)
    if query:
        results = results.filter(
            models.Q(Name__icontains=query) |
            models.Q(City__icontains=query) |
            models.Q(Significance__icontains=query)
        )

    if state:
        results = results.filter(State__iexact=state)

    elif place_type:
        results = results.filter(Type__iexact=place_type)

    else:
        results = results

    return render(
        request,
        'search-page.html',
        {'places': results, 'query': query, 'state': state, 'type': place_type}
    )

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        user_exists = User.objects.filter(username=username).exists()
        if user_exists:
            messages.error(request, 'Username allready exists')
            return redirect('/signup')
        if password1 == password2:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            return redirect('/')
        else:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})
    return render(request, 'signup.html')

# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'user does not exists')
            return redirect('/create-profile')
    return render(request, 'login.html')

# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')

gmaps = googlemaps.Client(key="AIzaSyAyUAkmbw3LUmZy5w15DmMFaVh3x-utvHw")
def get_distance(origin, destination):
    try:
        result = gmaps.distance_matrix(origins=origin, destinations=destination, mode="driving")
        element = result["rows"][0]["elements"][0]
        if element["status"] == "OK":
            distance = element["distance"]["value"]  # Distance in meters
            return distance / 1000  # Convert to kilometers
        else:
            return None
    except Exception as e:
        print(f"Error fetching distance: {e}")
        return None

@csrf_exempt
def estimate_cost(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            origin = data.get("origin")
            destination = data.get("destination")

            if not (origin and destination):
                return JsonResponse({"error": "Invalid input"}, status=400)

            # Calculate distance
            distance = get_distance(origin, destination)
            if distance is None:
                return JsonResponse({"error": "Could not fetch distance"}, status=500)

            # Calculate cost (example: ₹10 per km)
            car_cost = distance * 10
            train_cost = distance * 6
            air_cost = distance * 14

            return JsonResponse({"car_cost": int(car_cost), "train_cost" : int(train_cost), "air_cost" : int(air_cost)})
        except Exception as e:
            print(f"Error in API: {e}")
            return JsonResponse({"error": "Internal server error"}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

def submit_trip_review(request, pk):
    if request.user.is_authenticated:
        place = PlaceMode.objects.get(id=pk)
        if request.method == "POST":
            title = request.POST.get("title")
            description = request.POST.get("description")
            travel_medium = request.POST.get("travel_medium")
            travel_cost = request.POST.get("travel_cost")
            accommodation_cost = request.POST.get("accommodation_cost")
            food_cost = request.POST.get("food_cost")
            rating = request.POST.get("rating")


            # Create TripReview object
            TripReview.objects.create(
                title=title,
                description=description,
                travel_medium=travel_medium,
                travel_cost=travel_cost,
                accommodation_cost=accommodation_cost,
                food_cost=food_cost,
                user=request.user,
                place=place,
                rating=rating
            )

            messages.success(request, "Your trip review has been submitted!")
            return redirect(reverse("submit_trip_review", kwargs={"pk": place.id}))  # Redirect to the same page or another
    else:
        return redirect("/login")
    return render(request, "reviewform.html", {"single_place": place}) 

def create_profile(request):
    if request.method == "POST":
        full_name = request.POST.get("name")
        description = request.POST.get("description")
        state = request.POST.get("state")

        if not full_name or not description or not state:
            messages.error(request, "All fields are required.")
            return redirect("create_profile")

        user = request.user if request.user.is_authenticated else None

        profile, created = ProfileModel.objects.get_or_create(user=user)
        profile.state = state
        profile.description = description
        profile.save()

        messages.success(request, "Profile created successfully!")
        return redirect("/")

    return render(request, "profile_form.html")

def profile(request):
    if request.user.is_authenticated:
        if not ProfileModel.objects.filter(user=request.user).exists():
            return redirect("/create-profile")
        profile = ProfileModel.objects.get(user=request.user)
        reviews = None
        review_count = 0
        if TripReview.objects.filter(user=request.user).exists():
            reviews = TripReview.objects.filter(user=request.user)
            review_count = reviews.count()
            trophies = int(review_count / 2)
        return render(request, "profilepage.html", { "trophies": trophies, "profile": profile, "reviews": reviews, "count": review_count})

def stories(request):
    reviews = TripReview.objects.all()
    return render(request, "stories.html", {"reviews": reviews})

def about(request):
    return render(request, "about.html")