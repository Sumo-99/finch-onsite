import logging
import json
import os
import tempfile
from decimal import Decimal, InvalidOperation

from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Case, Client, Coverage, Damages
from .serializers import (
    AuthTokenRequestSerializer,
    CaseReportCaseSerializer,
    CaseReportClientSerializer,
    CaseReportCoverageSerializer,
    CaseReportDamagesSerializer,
    CaseReportSerializer,
)
from scripts.analysis import extract_structured_intake

logger = logging.getLogger(__name__)


@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok"})


def _save_uploaded_file_temporarily(uploaded_file):
    suffix = ".json"
    _, extension = os.path.splitext(uploaded_file.name or "")
    if extension:
        suffix = extension

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        for chunk in uploaded_file.chunks():
            temp_file.write(chunk)
    finally:
        temp_file.close()

    return temp_file.name


def _load_json_payload(file_path):
    with open(file_path, encoding="utf-8") as file_handle:
        payload = json.load(file_handle)

    if not isinstance(payload, dict):
        raise ValueError("Uploaded JSON must contain a top-level object.")

    return payload


def _delete_temp_file(file_path):
    if file_path and os.path.exists(file_path):
        os.remove(file_path)


def _parse_decimal(value):
    if value in (None, ""):
        return None

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _normalize_coverage_type(value):
    if value in {Coverage.CoverageType.FIRST_PARTY, Coverage.CoverageType.THIRD_PARTY}:
        return value
    return None


def _has_meaningful_damages_data(damages_data):
    return any(
        [
            damages_data.get("treatment_received") is True,
            damages_data.get("treatment_type"),
            damages_data.get("description"),
            damages_data.get("treatment_cost"),
        ]
    )


def _has_meaningful_coverage_data(coverage_data):
    return any(
        [
            _normalize_coverage_type(coverage_data.get("type")),
            coverage_data.get("policy_limit"),
            coverage_data.get("deductible"),
            coverage_data.get("insurer_name"),
        ]
    )


def _create_client_record(structured_output):
    client_data = structured_output.get("client", {})
    return Client.objects.create(
        name=client_data.get("name"),
        age=client_data.get("age"),
        email=client_data.get("email"),
        phone=client_data.get("phone"),
        liable=client_data.get("liable"),
        liable_reason=client_data.get("liable_reason"),
    )


def _create_case_record(user, client, structured_output):
    incident_data = structured_output.get("incident", {})
    recommendation_data = structured_output.get("recommendation", {})
    recommendation = recommendation_data.get("decision")
    if recommendation not in {
        Case.Recommendation.ACCEPT,
        Case.Recommendation.REJECT,
        Case.Recommendation.REVIEW,
    }:
        recommendation = None

    return Case.objects.create(
        user=user,
        client=client,
        incident_type=incident_data.get("type"),
        incident_summary=incident_data.get("summary"),
        recommendation=recommendation,
    )


def _create_damages_record(case, structured_output):
    damages_data = structured_output.get("damages", {})
    if not _has_meaningful_damages_data(damages_data):
        return None

    return Damages.objects.create(
        case=case,
        treatment_received=damages_data.get("treatment_received"),
        treatment_type=damages_data.get("treatment_type"),
        description=damages_data.get("description"),
        treatment_cost=_parse_decimal(damages_data.get("treatment_cost")),
    )


def _create_coverage_record(case, structured_output):
    coverage_data = structured_output.get("coverage", {})
    if not _has_meaningful_coverage_data(coverage_data):
        return None

    return Coverage.objects.create(
        case=case,
        type=_normalize_coverage_type(coverage_data.get("type")),
        policy_limit=_parse_decimal(coverage_data.get("policy_limit")),
        deductible=_parse_decimal(coverage_data.get("deductible")),
        insurer_name=coverage_data.get("insurer_name"),
    )


def _persist_extracted_intake(user, structured_output):
    logger.info("Starting persistence for extracted intake payload for user_id=%s.", user.id)

    with transaction.atomic():
        client = _create_client_record(structured_output)
        case = _create_case_record(user, client, structured_output)
        damages = _create_damages_record(case, structured_output)
        coverage = _create_coverage_record(case, structured_output)

    logger.info(
        "Finished persistence for extracted intake payload with case_id=%s client_id=%s user_id=%s.",
        case.id,
        client.id,
        user.id,
    )
    return {
        "case_id": case.id,
        "client_id": client.id,
        "damages_ids": [damages.id] if damages else [],
        "coverage_ids": [coverage.id] if coverage else [],
        "structured_output": structured_output,
    }


class CaseReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, case_id):
        logger.info("Fetching case report for case_id=%s user_id=%s.", case_id, request.user.id)
        case = get_object_or_404(
            Case.objects.select_related("client").prefetch_related("damages", "coverages"),
            pk=case_id,
            user=request.user,
        )

        damages = case.damages.first()
        coverage = case.coverages.first()
        payload = {
            "case": CaseReportCaseSerializer(case).data,
            "client": CaseReportClientSerializer(case.client).data,
            "damages": CaseReportDamagesSerializer(damages).data if damages else None,
            "coverage": CaseReportCoverageSerializer(coverage).data if coverage else None,
        }
        serializer = CaseReportSerializer(payload)

        logger.info(
            "Returning case report for case_id=%s with damages_present=%s coverage_present=%s.",
            case.id,
            damages is not None,
            coverage is not None,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuthTokenView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = AuthTokenRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request=request,
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        logger.info("Issued auth token for user_id=%s.", user.id)
        return Response({"token": token.key}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def intake_extract(request):
    uploaded_file = request.FILES.get("file")
    if uploaded_file is None:
        return Response(
            {"detail": "A JSON file upload is required in the 'file' field."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    temp_file_path = None

    try:
        temp_file_path = _save_uploaded_file_temporarily(uploaded_file)
        payload = _load_json_payload(temp_file_path)
        logger.info("Starting intake extraction API request for uploaded file=%s.", uploaded_file.name)
        structured_output = extract_structured_intake(payload)
    except json.JSONDecodeError:
        return Response(
            {"detail": "Uploaded file did not contain valid JSON."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except ValueError as exc:
        return Response(
            {"detail": str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception:
        logger.exception("Failed during intake extraction helper execution.")
        return Response(
            {"detail": "Failed to process uploaded transcript."},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    finally:
        _delete_temp_file(temp_file_path)

    try:
        response_payload = _persist_extracted_intake(request.user, structured_output)
    except Exception:
        logger.exception("Failed while persisting extracted intake data.")
        return Response(
            {"detail": "Failed to persist extracted transcript data."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(response_payload, status=status.HTTP_200_OK)
