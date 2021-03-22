import uuid
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    FileField,
    ForeignKey,
    IntegerField,
    IntegerChoices,
    Model,
    UUIDField,
)
from django.core.validators import FileExtensionValidator


class Job(Model):


    class Priority(IntegerChoices):
        LOW = -1, "low"
        NORMAL = 0, "normal"
        HIGH = 1, "high"


    priority = IntegerField(choices=Priority.choices, default=Priority.NORMAL,)

    uuid = UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

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
    status = CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_QUEUED, null=False
    )
    user = ForeignKey("user_app.User", on_delete=CASCADE)
    in_file = FileField(
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
