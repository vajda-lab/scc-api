import uuid
from django.db import models
from django.core.validators import FileExtensionValidator


class Priority(models.IntegerChoices):
    LOW = (0, "low")
    NORMAL = (1, "normal")
    HIGH = (2, "high")


class Job(models.Model):


    priority = models.IntegerField(choices=Priority.choices, default=Priority.LOW,)

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    # STATUS_QUEUED = model instance created in Django
    # STATUS_ACTIVE = model instance sent to Celery
    STATUS_ACTIVE = "active"
    STATUS_COMPLETE = "complete"
    STATUS_ERROR = "error"
    STATUS_DELETED = "deleted"
    STATUS_QUEUED = "queued"
    STATUS_CHOICES = (
        (STATUS_ACTIVE, "active"),
        (STATUS_COMPLETE, "complete"),
        (STATUS_ERROR, "error"),
        (STATUS_DELETED, "deleted"),
        (STATUS_QUEUED, "queued"),
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_QUEUED, null=False
    )
    user = models.ForeignKey("user_app.User", on_delete=models.CASCADE)
    in_file = models.FileField(
        upload_to="jobs/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "PDB",
                ],
                message="Please upload a pdb file",
            )
        ],
    )

    class Meta:
        get_latest_by = ["created"]
        ordering = ["-created"]
