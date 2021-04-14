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
    # input_file will be INPUT TAR file
    # making sure input file path is accessible to other machines? Combined containers should fix this
    # Are these all (Django/submit host/SCC) running on the same server, or separate servers
    #ToDo: If file fails validation, put filename in the message
    input_file = models.FileField(
        upload_to="jobs_input/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "tar.bz2",
                    "tar.gz",
                    "tar.xz",
                    "bz2",
                    "gz",
                    "xz",
                ],
                message="Please upload a compressed TAR file",
            )
        ],
    )
    # output_file will be results TAR file
    #ToDo: If file fails validation, put filename in the message
    output_file = models.FileField(
        upload_to="jobs_output/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "tar.bz2",
                    "tar.gz",
                    "tar.xz",
                    "bz2",
                    "gz",
                    "xz",
                ],
                message="Please upload a compressed TAR file",
            )
        ],
    )
    sge_task_id = models.IntegerField(blank=True, null=True,)

    class Meta:
        get_latest_by = ["created"]
        ordering = ["-created"]

# ToDo: Create new model to log changes to Job (JobLog or better name)
# Also look breifly into Python's built-in auditing features
# https://docs.python.org/3/library/sys.html#auditing
# https://docs.python.org/3/library/audit_events.html#audit-events
# There are also some Django & DRF audit packages, but that may be more complexity than we need  
