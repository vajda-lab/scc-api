import uuid
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    FileField,
    ForeignKey,
    Model,
    UUIDField,
)
from django.core.validators import FileExtensionValidator


class Job(Model):
    uuid = UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    STATUS_COMPLETE = "complete"
    STATUS_ACTIVE = "active"
    STATUS_ERROR = "error"
    STATUS_DELETED = "deleted"
    STATUS_CHOICES = (
        (STATUS_COMPLETE, "complete"),
        (STATUS_ACTIVE, "active"),
        (STATUS_ERROR, "error"),
        (STATUS_DELETED, "deleted"),
    )
    status = CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE, null=False
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
