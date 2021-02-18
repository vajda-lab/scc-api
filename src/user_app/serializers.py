from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = [
            "affiliation",
            "organization",
            "notes",
            "max_job_submission"
        ]
