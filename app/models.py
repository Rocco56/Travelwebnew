from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class PlaceMode(models.Model):
    place_id = models.IntegerField(null=True, blank=True)
    Name = models.CharField(max_length=200, null=True, blank=True)
    City = models.CharField(max_length=200, blank=True, null=True)
    Zone = models.CharField(max_length=200, blank=True, null=True)
    Type = models.CharField(max_length=200, blank=True, null=True)
    State = models.CharField(max_length=200, null=True, blank=True)
    Description = models.CharField(max_length=200, null=True, blank=True)
    Year = models.CharField(max_length=200, null=True, blank=True)
    Time_needed = models.CharField(max_length=200, null=True, blank=True)
    Google_rating = models.CharField(max_length=200, null=True, blank=True)
    Significance = models.CharField(max_length=200, null=True, blank=True)
    Best_time_to_visit = models.CharField(max_length=200, null=True, blank=True)
    Fees = models.CharField(max_length=200, null=True, blank=True)
    Image_url = models.URLField(max_length=30000, null=True, blank=True)
    crowd = models.ForeignKey("CrowdModel", on_delete=models.CASCADE, null=True, blank=True)
    map_url = models.TextField(null=True, blank=True, db_column="map_url")

    def __str__(self):
        return self.Name

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    you_City = models.CharField(max_length=200, null=True, blank=True)
    you_State = models.CharField(max_length=200, null=True, blank=True)
    fav_type = models.CharField(max_length=200, null=True, blank=True)
    fav_significance  = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.user.username

class CrowdModel(models.Model):
    location = models.ForeignKey(PlaceMode, on_delete=models.CASCADE, null=True, blank=True) 
    month = models.IntegerField(null=True, blank=True)  
    crowd_count = models.IntegerField(null=True, blank=True)  
    month_name = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        unique_together = ('location', 'month')  # Ensure unique crowd data for each month/year and location

    def __str__(self):
        return f"Crowd data for {self.location} in {self.month_name}" 
    

class ReviewModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    place = models.ForeignKey(PlaceMode, on_delete=models.CASCADE, null=True, blank=True)
    review_text = models.CharField(max_length=50, null=True, blank=True)
    review_description = models.TextField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    rating = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"user {self.user.username}'s review to {self.place.Name}"


class TripReview(models.Model):
    TRAVEL_MEDIUM_CHOICES = [
        ('flight', 'Flight'),
        ('train', 'Train'),
        ('bus', 'Bus'),
        ('car', 'Car'),
        ('ship', 'Ship'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    place = models.ForeignKey(PlaceMode, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    travel_medium = models.CharField(max_length=10, choices=TRAVEL_MEDIUM_CHOICES, null=True, blank=True)
    travel_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    accommodation_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    food_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title

class ProfileModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    review = models.ForeignKey(TripReview, on_delete=models.CASCADE, null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    trophies = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username  


