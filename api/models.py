from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=20, unique=True)
    member_one = models.CharField(max_length=20, unique=True)
    member_two = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TournamentGroup(models.Model):
    name = models.CharField(max_length=10, blank=True)
    teams = models.ManyToManyField(Team)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.name:
            existing_count = TournamentGroup.objects.count()
            self.name = f"Group {existing_count + 1}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
