from django.db import models
from django.utils import timezone
from improved_user.model_mixins import AbstractUser
from sccApi.models import Job, Priority
import datetime


AFFILIATION_CHOICES = (
    ("I", "Industry"),
    ("A", "Academia"),
    ("O", "Other"),
)

# yesterday = datetime.date.today() - datetime.timedelta(days=1)
# orders = Order.objects.filter(date__gt=yesterday)


# Create your models here.
class User(AbstractUser):
    """A User model that extends the Improved User"""

    affiliation = models.CharField(
        max_length=1, choices=AFFILIATION_CHOICES, default="O", null=False
    )
    organization = models.CharField(max_length=250)
    notes = models.CharField(max_length=1000, blank=True, null=True)
    max_job_submission = models.IntegerField(default=20)
    priority = models.IntegerField(
        choices=Priority.choices,
        default=Priority.LOW,
    )

    def daily_job_count(self):
        return (
            Job.objects.filter(user=self.pk)
            .filter(created_at__gt=timezone.now())
            .count()
        )
