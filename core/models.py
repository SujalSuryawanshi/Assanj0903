from django.db import models
from datetime import datetime,date
from Main import settings
from django.urls import reverse
from embed_video.fields import EmbedVideoField
from users.models import CustomUser




class Category(models.Model):
    cat_name=models.CharField(max_length=30, null=True, blank=True)
    def __str__(self):
        return self.cat_name

class Egit(models.Model):
    egit_name=models.CharField(max_length=30)
    def __str__(self):
        return self.egit_name
    
class Subcat(models.Model):
    sub_cat=models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_name=models.CharField(max_length=30, null=True, blank=True)
    def __str__(self):
        return self.sub_name
        
class Staller(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=300)
    address = models.CharField(max_length=400)
    category = models.ManyToManyField(Category, related_name='categor')
    video = EmbedVideoField(null=True)
    egit = models.ForeignKey(Egit, on_delete=models.CASCADE, null=True, blank=True)
    contact = models.CharField(max_length=12, default='1234')
    timings = models.CharField(max_length=14)
    rating = models.FloatField(default=0)
    keywords = models.CharField(max_length=1000, default='spicy', null=True)
    likes = models.PositiveIntegerField(default=0)

    location_accuracy = models.BooleanField(default=False)  # Yes or No
    surrounding_landmarks = models.TextField(blank=True, null=True)
    owner_behaviour = models.CharField(max_length=10, choices=[
        ('bad', 'Bad'),
        ('average', 'Average'),
        ('good', 'Good'),
        ('great', 'Great'),
    ])
    locality_preferred_for = models.CharField(max_length=10, choices=[
        ('family', 'Family'),
        ('friends', 'Friends'),
        ('couples', 'Couples'),
    ])
    locality_visited_with = models.CharField(max_length=10, choices=[
        ('family', 'Family'),
        ('friends', 'Friends'),
        ('couples', 'Couples'),
    ])

    def __str__(self):
        return self.name

    def update_rating(self):
        ratings = self.ratings.all()  # Use related name
        avg_rating = sum(r.rating for r in ratings) / len(ratings) if ratings else 0
        self.rating = avg_rating
        self.save()
    def get_absolute_url(self):
        return reverse("detail", kwargs={"name": self.name})
    

class Rating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    staller = models.ForeignKey(Staller, related_name='ratings', on_delete=models.CASCADE)
    rating = models.IntegerField(default=1)

    class Meta:
        unique_together = ('user', 'staller')

    def __str__(self):
        return f'{self.user} - {self.staller} - {self.rating}'
    
class Foo_Category(models.Model):
    sh_owner=models.ForeignKey(Staller, on_delete=models.CASCADE, default='')
    foo_name=models.CharField(max_length=30, null=True)
    def __str__(self):
        return self.foo_name


class MenuItems(models.Model):
    owner = models.ForeignKey(Staller, on_delete=models.CASCADE, null=True, related_name='menu_items')
    menu_photo = models.ImageField(upload_to='static/images/menu_pics/', null=True, blank=True)
    name = models.CharField(max_length=200)
    foo_cat = models.ForeignKey(Foo_Category, on_delete=models.SET_NULL, null=True)
    normal_price = models.CharField(max_length=100, null=True, blank=True,default='0')
    premium_price = models.CharField(max_length=100, null=True, blank=True,default='0')
    description=models.CharField(max_length=200, null=True, blank=True)
    stock=models.IntegerField(null=True,blank=True)
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.name

    def update_rating(self):
        foo_ratings = self.foo_ratings.all()  # Use related name
        avg_rating = sum(r.rating for r in foo_ratings) / len(foo_ratings) if foo_ratings else 0
        self.rating = avg_rating
        self.save()


class FooRating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    menu = models.ForeignKey(MenuItems, related_name='foo_ratings', on_delete=models.CASCADE)
    rating = models.IntegerField(default=1)

    class Meta:
        unique_together = ('user', 'menu')

    def __str__(self):
        return f'{self.user} - {self.menu} - {self.rating}'



class Following(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='following')
    staller = models.ForeignKey(Staller, on_delete=models.CASCADE, related_name='followers')

    class Meta:
        unique_together = ('user', 'staller') 

    def __str__(self):
        return f'{self.user.username} follows {self.staller.name}'
    


class New_offer(models.Model):
    owner=models.ForeignKey(Staller,on_delete=models.CASCADE, related_name='offers')
    title=models.CharField(max_length=100)
    offer_photo = models.ImageField(upload_to='static/images/offer_pics/')
    message=models.CharField(max_length=10000)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Rater(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.IntegerField(default=100)
    description = models.CharField(max_length=600)
    img_link = models.CharField(max_length=1000)
    aff_link = models.CharField(max_length=300)
    keywords = models.CharField(max_length=300)
    rat_cat=models.ForeignKey(Foo_Category,on_delete=models.CASCADE)
    likes = models.ManyToManyField(CustomUser, related_name="liked_raters", blank=True)
    ratings = models.ManyToManyField(CustomUser, through='Review', related_name="rated_raters", blank=True)


    def total_likes(self):
        return self.likes.count()

    def average_rating(self):
        ratings = self.review_set.all()
        return sum(review.rating for review in ratings) / len(ratings) if ratings else 0

    def __str__(self):
        return self.name
    def number_of_reviews(self):
        return self.review_set.count()

class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rater = models.ForeignKey(Rater, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'rater')



class UserLike(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    staller = models.ForeignKey(Staller, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'staller')  # Ensure a user can like the same staller only once




