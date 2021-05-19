import uuid

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Priority(models.IntegerChoices):
    LOW = (0, "low")
    NORMAL = (1, "normal")
    HIGH = (2, "high")


class Status(models.TextChoices):
    # Status.ACTIVE = model instance sent to Celery
    # Status.COMPLETE = job complete on SCC; compress, capture, & delete SCC dir
    # Status.DELETED = See bin.submit_host_cli.delete()
    # Status.ERROR = job errored on SCC; compress, capture, & delete SCC dir
    # Status.QUEUED = model instance created in Django
    ACTIVE = "active", _("active")
    COMPLETE = "complete", _("complete")
    DELETED = "deleted", _("deleted")
    ERROR = "error", _("error")
    QUEUED = "queued", _("queued")


class JobQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=Status.ACTIVE)

    def complete(self):
        return self.filter(status=Status.COMPLETE)

    def deleted(self):
        return self.filter(status=Status.DELETED)

    def error(self):
        return self.filter(status=Status.ERROR)

    def queued(self):
        return self.filter(status=Status.QUEUED)

    def high_priority(self):
        return self.filter(priority=Priority.HIGH)

    def low_priority(self):
        return self.filter(priority=Priority.LOW)

    def normal_priority(self):
        return self.filter(priority=Priority.NORMAL)


class Job(models.Model):
    priority = models.IntegerField(
        choices=Priority.choices,
        default=Priority.LOW,
    )
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.QUEUED,
        null=False,
        db_index=True,
    )
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    # input_file will be INPUT TAR file
    # making sure input file path is accessible to other machines? Combined containers should fix this
    # Are these all (Django/submit host/SCC) running on the same server, or separate servers
    # ToDo: If file fails validation, put filename in the message
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
    # ToDo: If file fails validation, put filename in the message
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
    sge_task_id = models.IntegerField(
        blank=True,
        null=True,
    )

    # these are to track what comes out of qstat
    # state The state of the job:
    #   (r) – running;
    #   (qw) – waiting to run;
    #   (hqw) – on hold, waiting to run;
    #   (Eqw) – job in error state;
    #   (s) – suspended;
    #   (t) – transfering.
    job_state = models.CharField(max_length=10, blank=True, null=True)
    job_submitted = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Time when the job was submitted. When the job is running, this field is updated with the time the job started.",
    )
    job_data = models.JSONField(default=dict, blank=True)
    job_ja_task_id = models.IntegerField(
        blank=True,
        null=True,
    )

    objects = JobQuerySet.as_manager()

    class Meta:
        get_latest_by = ["created"]
        ordering = ["-created"]

    def __str__(self):
        return f"{self.uuid}: {self.status}"


# Also look breifly into Python's built-in auditing features
# https://docs.python.org/3/library/sys.html#auditing
# https://docs.python.org/3/library/audit_events.html#audit-events
# There are also some Django & DRF audit packages, but that may be more complexity than we need
class JobLog(models.Model):
    job = models.ForeignKey("Job", on_delete=models.CASCADE)
    event = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    # TODO: We may want a user?
    # user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    class Meta:
        get_latest_by = ["created"]
        ordering = ["-created"]

    def __str__(self):
        return f"{self.pk}: {self.event}"
