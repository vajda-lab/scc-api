from rest_framework import serializers

from .models import Job


class JobSerializer(serializers.ModelSerializer):
    """Serializer for Job model."""

    user_email = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            "uuid",
            "status",
            "user",
            "input_file",
            "output_file",
            "sge_task_id",
            "job_state",
            "job_data",
            "user_email",
        ]

    def get_user_email(self, obj):
        return obj.user.email
