from django.forms import ModelForm, ValidationError
import requests

from .models import Job


class JobSubmitform(ModelForm):
    class Meta(object):
        model = Job
        fields = ["title", "pdb_id", "chain", "in_file"]

    def clean(self):
        cleaned_data = super().clean()
        pdb_id = cleaned_data.get('pdb_id')
        if pdb_id:
            if len(pdb_id) !=4:
                raise ValidationError('Please enter a valid PDB ID', code='invalid')
            url = "https://files.rcsb.org/download/{}.pdb".format(pdb_id)
            r = requests.get(url)
            if not r.status_code == 200:
                raise ValidationError('Please enter a valid PDB ID', code='invalid')
        return cleaned_data


class JobAdminForm(ModelForm):
    class Meta:
        model = Job
        fields = ('__all__' )

    def clean(self):
        cleaned_data = super().clean()
        pdb_id = cleaned_data.get('pdb_id')
        if pdb_id:
            if len(pdb_id) !=4:
                raise ValidationError('Please enter a valid PDB ID', code='invalid')
            url = "https://files.rcsb.org/download/{}.pdb".format(pdb_id)
            r = requests.get(url)
            if not r.status_code == 200:
                raise ValidationError('Please enter a valid PDB ID', code='invalid')
        return cleaned_data

