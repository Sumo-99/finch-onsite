from rest_framework import serializers


class CaseReportCaseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.CharField()
    incident_type = serializers.CharField(allow_null=True)
    incident_summary = serializers.CharField(allow_null=True)
    recommendation = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()


class CaseReportClientSerializer(serializers.Serializer):
    name = serializers.CharField(allow_null=True)
    age = serializers.IntegerField(allow_null=True)
    email = serializers.EmailField(allow_null=True)
    phone = serializers.CharField(allow_null=True)
    liable = serializers.BooleanField(allow_null=True)
    liable_reason = serializers.CharField(allow_null=True)


class CaseReportDamagesSerializer(serializers.Serializer):
    treatment_received = serializers.BooleanField(allow_null=True)
    treatment_type = serializers.CharField(allow_null=True)
    description = serializers.CharField(allow_null=True)
    treatment_cost = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        allow_null=True,
    )


class CaseReportCoverageSerializer(serializers.Serializer):
    type = serializers.CharField(allow_null=True)
    insurer_name = serializers.CharField(allow_null=True)
    policy_limit = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        allow_null=True,
    )
    deductible = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        allow_null=True,
    )


class CaseReportSerializer(serializers.Serializer):
    case = CaseReportCaseSerializer()
    client = CaseReportClientSerializer()
    damages = CaseReportDamagesSerializer(allow_null=True)
    coverage = CaseReportCoverageSerializer(allow_null=True)


class AuthTokenRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
