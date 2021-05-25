from rest_framework import serializers

from .models import Job


class JobSerializer(serializers.ModelSerializer):
    """Serializer for Job model."""

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
        ]
