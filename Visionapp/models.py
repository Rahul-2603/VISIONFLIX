from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
import uuid
from django.conf import settings
# Create your models here.
MOVIE_CHOICES = (
    ('movie', 'movie'),
    ('series', 'series'),
)

AGE_CHOICES = (
    ('All', 'All'),
    ('Kids', 'Kids'),
)

class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    profiles = models.ManyToManyField('Profile', blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()


   

class Profile(models.Model):
    name = models.CharField(max_length=1000 ,unique=True)
    age_limit = models.CharField(choices=AGE_CHOICES, max_length=10)
    uuid = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        return self.name


class Movie(models.Model):

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    poster = models.CharField(max_length=255)
    backdrop = models.CharField(max_length=255)
    rating = models.FloatField(null=True)
    release_date = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=10)
    popularity = models.FloatField(null=True)
    genre = models.CharField(max_length=200)
    def __str__(self):
        return self.title
    
class Movielist(models.Model):
    profile= models.ForeignKey(Profile, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('profile', 'movie')

    def __str__(self):
        return f"{self.profile} - {self.movie}"



class Cast(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="casts")
    name = models.CharField(max_length=200)
    character = models.CharField(max_length=200)
    image = models.CharField(max_length=255)
    def __str__(self):
        return self.name
      
    
class Video(models.Model):
    movie = models.ForeignKey(Movie, related_name="video", on_delete=models.CASCADE)
    file = models.FileField(upload_to="videos/")
    def __str__(self):
        return self.movie.title
