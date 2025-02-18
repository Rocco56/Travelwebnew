from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index, name="index"),
    path('details/<int:pk>/', views.details, name="details"),
    path('search', views.search_view, name='search'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('estimate-cost/', views.estimate_cost, name='estimate-cost'),
    path("submit-review/", views.submit_trip_review, name="submit_trip_review"),
    # path('', include('app.urls'))
]
