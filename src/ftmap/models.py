import uuid
from django.db.models import (
CASCADE,
CharField,
DateTimeField,
FileField,
ForeignKey,
Model,
UUIDField
)
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.core.files import File
from urllib.request import urlopen
from tempfile import NamedTemporaryFile

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
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        null=False)
    pdb_id = CharField(max_length=4, blank=True, null=True)
    chain = CharField(max_length=1, blank=True, null=True)
    title = CharField(max_length=70, blank=True, null=True)
    user = ForeignKey('user_app.User', on_delete=CASCADE)
    in_file = FileField(upload_to="jobs/",
                               blank=True,
                               null=True,
                               validators=[FileExtensionValidator(allowed_extensions=['PDB',],
                                                                  message='Please upload a pdb file')])

    class Meta:
        get_latest_by = ["created"]
        ordering = ["-created"]


    def clean(self):
        if not self.pdb_id and not self.in_file:  # This will check for None or Empty
            raise ValidationError('Please enter a PDB id or upload a pdb file.')


    def save(self, *args, **kwargs):
        # uppercase the pdb id
        if self.pdb_id:
            self.pdb_id = self.pdb_id.upper()
        # download the pdb file
        if self.pdb_id and not self.in_file:
            img_temp = NamedTemporaryFile(delete=True)
            url = "https://files.rcsb.org/download/{}.pdb".format(self.pdb_id)
            img_temp.write(urlopen(url).read())
            img_temp.flush()
            self.in_file.save(f"job_{self.uuid}.pdb", File(img_temp))

        # if no title given
        if not self.title:
            # use pdb id if given
            if self.pdb_id:
                self.title = self.pdb_id
            else:
                # use filename
                self.title = "{}".format(self.in_file.name.split('/')[-1])
        super(Job, self).save(*args, **kwargs)



    def __unicode__(self):
        return self.title



class Example(Model):
    title = CharField(max_length=100)
    pdb_id = CharField(max_length=4)
    pdb_file = FileField(upload_to="examples/")
    pse_file = FileField(upload_to="examples/")