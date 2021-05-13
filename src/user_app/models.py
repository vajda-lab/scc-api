from django.db import models
from django.utils import timezone
from improved_user.model_mixins import AbstractUser

from sccApi.models import Job, Priority


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
