# Generated by Django 3.1.7 on 2021-04-14 20:32

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sccApi', '0016_auto_20210413_1927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='input_file',
            field=models.FileField(blank=True, null=True, upload_to='jobs_input/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['tar.xz', 'tar.gz', 'tar.bz2', 'xz'], message='Please upload a compressed TAR file')]),
        ),
    ]
