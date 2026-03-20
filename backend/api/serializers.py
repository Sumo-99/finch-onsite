from django.utils import timezone
from django.db import transaction
from rest_framework import serializers

from .models import Case, CaseLog, Client, User


class CaseLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseLog
        fields = ["log_id", "timestamp", "stage", "description"]


class CaseListSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Case
        fields = [
            "case_id",
            "start_date",
            "intake_date",
            "incident_type",
            "insurance_company_name",
            "status",
            "stage",
            "client",
            "client_name",
            "user",
            "user_email",
        ]


class CaseDetailSerializer(serializers.ModelSerializer):
    logs = CaseLogSerializer(many=True, read_only=True)
    client_name = serializers.CharField(source="client.name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Case
        fields = [
            "case_id",
            "start_date",
            "intake_date",
            "incident_type",
            "insurance_company_name",
            "status",
            "stage",
            "client",
            "client_name",
            "user",
            "user_email",
            "logs",
        ]


class CaseCreateSerializer(serializers.Serializer):
    client_name = serializers.CharField(max_length=255)
    client_email = serializers.EmailField()
    incident_date = serializers.DateField()
    incident_type = serializers.CharField(max_length=255)
    insurance_company_name = serializers.CharField(max_length=255)

    @transaction.atomic
    def create(self, validated_data):
        client_name = validated_data["client_name"]
        client_email = validated_data["client_email"]
        incident_date = validated_data["incident_date"]
        incident_type = validated_data["incident_type"]
        insurance_company_name = validated_data["insurance_company_name"]

        print(
            "[CaseCreateSerializer.create] Starting intake case creation for "
            f"{client_email}."
        )

        client, created = Client.objects.get_or_create(
            email=client_email,
            defaults={
                "name": client_name,
                "phone_number": "",
            },
        )
        if created:
            print(
                "[CaseCreateSerializer.create] Created client "
                f"{client.client_id} for {client_email}."
            )
        else:
            print(
                "[CaseCreateSerializer.create] Reusing client "
                f"{client.client_id} for {client_email}."
            )

        owner = User.objects.order_by("user_id").first()
        if owner is None:
            print(
                "[CaseCreateSerializer.create] Aborting case creation because no "
                "users exist."
            )
            raise serializers.ValidationError("No intake owner is available.")

        print(
            "[CaseCreateSerializer.create] Assigning default owner "
            f"{owner.user_id} to the case."
        )

        case = Case.objects.create(
            start_date=timezone.localdate(),
            intake_date=incident_date,
            incident_type=incident_type,
            insurance_company_name=insurance_company_name,
            status=Case.Status.ACTIVE,
            stage=Case.Stage.INTAKE,
            client=client,
            user=owner,
        )

        print(
            "[CaseCreateSerializer.create] Created case "
            f"{case.case_id} with start_date={case.start_date} "
            f"and intake_date={case.intake_date}."
        )

        return case


class CaseStageAdvanceSerializer(serializers.Serializer):
    description = serializers.CharField(required=False, allow_blank=True)
