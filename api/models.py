from django.db import models
from django.contrib.auth.models import User


class Team(models.Model):
    name = models.CharField(max_length=20, unique=True)
    member_one = models.CharField(max_length=20, unique=True)
    member_two = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teams")

    def __str__(self):
        return self.name
