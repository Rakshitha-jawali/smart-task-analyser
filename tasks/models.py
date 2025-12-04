from django.db import models

# Create your models here.

class Task(models.Model):
    title = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)
    importance = models.IntegerField(default=5)  # 1-10
    estimated_hours = models.IntegerField(default=1)
    dependencies = models.JSONField(default=list, blank=True)  # list of dependency identifiers (IDs or titles)
    done = models.BooleanField(default=False)

    def __str__(self):
        return self.title
