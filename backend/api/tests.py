from decimal import Decimal
import json
from unittest.mock import patch

from django.apps import apps
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import ProtectedError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase


class CaseDataModelTests(TestCase):
    def get_model(self, model_name):
        try:
            return apps.get_model("api", model_name)
        except LookupError as exc:
            self.fail(f"Expected api.{model_name} model to exist: {exc}")

    def test_auth_uses_api_user_model(self):
        self.assertEqual(settings.AUTH_USER_MODEL, "api.User")

    def test_user_can_be_created_with_email_login(self):
        user_model = self.get_model("User")

        user = user_model.objects.create_user(
            email="adjuster@example.com",
            password="test-pass-123",
        )

        self.assertEqual(user.email, "adjuster@example.com")
        self.assertTrue(user.check_password("test-pass-123"))

    def test_case_defaults_and_nullable_fields(self):
        user_model = self.get_model("User")
        client_model = self.get_model("Client")
        case_model = self.get_model("Case")

        user = user_model.objects.create_user(
            email="owner@example.com",
            password="test-pass-123",
        )
        client = client_model.objects.create(liable=None)

        case = case_model.objects.create(user=user, client=client)

        self.assertEqual(case.status, case_model.Status.ACTIVE)
        self.assertIsNone(case.recommendation)
        self.assertIsNone(case.incident_type)
        self.assertIsNone(case.incident_summary)
        self.assertIsNotNone(case.created_at)
        self.assertIsNone(client.name)
        self.assertIsNone(client.age)
        self.assertIsNone(client.email)
        self.assertIsNone(client.phone)
        self.assertIsNone(client.liable)

    def test_case_supports_multiple_damage_and_coverage_rows(self):
        user_model = self.get_model("User")
        client_model = self.get_model("Client")
        case_model = self.get_model("Case")
        damages_model = self.get_model("Damages")
        coverage_model = self.get_model("Coverage")

        user = user_model.objects.create_user(
            email="case-owner@example.com",
            password="test-pass-123",
        )
        client = client_model.objects.create()
        case = case_model.objects.create(user=user, client=client)

        damages_model.objects.create(
            case=case,
            treatment_received=True,
            treatment_type="Physical therapy",
            description="First treatment block",
            treatment_cost=Decimal("1250.50"),
        )
        damages_model.objects.create(case=case, treatment_received=False)

        coverage_model.objects.create(
            case=case,
            type=coverage_model.CoverageType.FIRST_PARTY,
            policy_limit=Decimal("50000.00"),
            deductible=Decimal("1000.00"),
            insurer_name="Carrier A",
        )
        coverage_model.objects.create(
            case=case,
            type=coverage_model.CoverageType.THIRD_PARTY,
        )

        self.assertEqual(case.damages.count(), 2)
        self.assertEqual(case.coverages.count(), 2)

    def test_deleting_user_or_client_with_cases_is_protected(self):
        user_model = self.get_model("User")
        client_model = self.get_model("Client")
        case_model = self.get_model("Case")

        user = user_model.objects.create_user(
            email="protected@example.com",
            password="test-pass-123",
        )
        client = client_model.objects.create()
        case_model.objects.create(user=user, client=client)

        with self.assertRaises(ProtectedError):
            user.delete()

        with self.assertRaises(ProtectedError):
            client.delete()

    def test_deleting_case_cascades_to_damages_and_coverages(self):
        user_model = self.get_model("User")
        client_model = self.get_model("Client")
        case_model = self.get_model("Case")
        damages_model = self.get_model("Damages")
        coverage_model = self.get_model("Coverage")

        user = user_model.objects.create_user(
            email="cascade@example.com",
            password="test-pass-123",
        )
        client = client_model.objects.create()
        case = case_model.objects.create(user=user, client=client)

        damages_model.objects.create(case=case)
        coverage_model.objects.create(case=case)

        case.delete()

        self.assertEqual(damages_model.objects.count(), 0)
        self.assertEqual(coverage_model.objects.count(), 0)


class IntakeExtractionApiTests(APITestCase):
    def test_post_uploaded_json_file_returns_structured_output(self):
        payload = {
            "id": "call-123",
            "transcript": [
                {"speaker": "Agent", "text": "Tell me what happened."},
                {"speaker": "Caller", "text": "I was rear-ended at a stoplight."},
            ],
        }
        uploaded_file = SimpleUploadedFile(
            "transcript.json",
            json.dumps(payload).encode("utf-8"),
            content_type="application/json",
        )
        structured_output = {
            "client": {"name": "Jane Doe", "age": None, "email": None, "phone": None, "liable": None},
            "incident": {"type": "Auto accident", "summary": "Rear-end collision."},
            "damages": {
                "treatment_received": False,
                "treatment_type": None,
                "description": None,
                "treatment_cost": None,
            },
            "coverage": {"type": None, "policy_limit": None, "deductible": None, "insurer_name": None},
            "recommendation": {"decision": "REVIEW", "reason": "Needs further review."},
        }

        with patch("api.views.extract_structured_intake", return_value=structured_output) as extraction_mock:
            response = self.client.post("/api/intake-extract/", {"file": uploaded_file}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), structured_output)
        extraction_mock.assert_called_once_with(payload)

    def test_post_without_file_returns_bad_request(self):
        response = self.client.post("/api/intake-extract/", {}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"detail": "A JSON file upload is required in the 'file' field."})

    def test_post_with_malformed_json_file_returns_bad_request(self):
        uploaded_file = SimpleUploadedFile(
            "transcript.json",
            b"{not valid json}",
            content_type="application/json",
        )

        response = self.client.post("/api/intake-extract/", {"file": uploaded_file}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"detail": "Uploaded file did not contain valid JSON."})
