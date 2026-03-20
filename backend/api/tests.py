from decimal import Decimal
import json
from unittest.mock import patch

from django.apps import apps
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import ProtectedError
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from scripts.analysis import LEGAL_INTAKE_PROMPT, _normalize_structured_output


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
        self.assertIsNone(client.liable_reason)

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


class LegalIntakePromptTests(TestCase):
    def test_prompt_includes_explicit_recommendation_decision_rules(self):
        self.assertIn("Use these rules in order to determine recommendation.decision:", LEGAL_INTAKE_PROMPT)
        self.assertIn("Always apply REJECT before ACCEPT.", LEGAL_INTAKE_PROMPT)
        self.assertIn("If both conditions appear to be met, prefer REJECT.", LEGAL_INTAKE_PROMPT)
        self.assertIn("When in doubt, use REVIEW over ACCEPT.", LEGAL_INTAKE_PROMPT)

    def test_prompt_includes_explicit_coverage_insurer_inference_rules(self):
        self.assertIn('"insurer_inferred": boolean', LEGAL_INTAKE_PROMPT)
        self.assertIn("Set insurer_name only when the caller explicitly states the name", LEGAL_INTAKE_PROMPT)
        self.assertIn("Set insurer_inferred to true if insurer_name was implied", LEGAL_INTAKE_PROMPT)
        self.assertIn("Set insurer_inferred to false if insurer_name was explicitly stated by the caller.", LEGAL_INTAKE_PROMPT)
        self.assertIn("Set insurer_inferred to false if insurer_name is null.", LEGAL_INTAKE_PROMPT)


class IntakeNormalizationTests(TestCase):
    def test_normalize_structured_output_defaults_insurer_inferred_to_false(self):
        normalized = _normalize_structured_output(
            {
                "coverage": {
                    "type": None,
                    "policy_limit": None,
                    "deductible": None,
                    "insurer_name": None,
                }
            }
        )

        self.assertFalse(normalized["coverage"]["insurer_inferred"])

    def test_normalize_structured_output_preserves_true_insurer_inferred(self):
        normalized = _normalize_structured_output(
            {
                "coverage": {
                    "type": None,
                    "policy_limit": None,
                    "deductible": None,
                    "insurer_name": "Potential carrier",
                    "insurer_inferred": True,
                }
            }
        )

        self.assertTrue(normalized["coverage"]["insurer_inferred"])

    def test_normalize_structured_output_forces_false_insurer_inferred_when_name_is_null(self):
        normalized = _normalize_structured_output(
            {
                "coverage": {
                    "type": None,
                    "policy_limit": None,
                    "deductible": None,
                    "insurer_name": None,
                    "insurer_inferred": True,
                }
            }
        )

        self.assertFalse(normalized["coverage"]["insurer_inferred"])


class IntakeExtractionApiTests(APITestCase):
    def get_model(self, model_name):
        try:
            return apps.get_model("api", model_name)
        except LookupError as exc:
            self.fail(f"Expected api.{model_name} model to exist: {exc}")

    def build_upload(self, payload):
        return SimpleUploadedFile(
            "transcript.json",
            json.dumps(payload).encode("utf-8"),
            content_type="application/json",
        )

    def create_user(self, email="sumanth@suits.com"):
        user_model = self.get_model("User")
        return user_model.objects.create_user(email=email, password="123")

    def test_post_uploaded_json_file_persists_records_and_returns_ids(self):
        user_model = self.get_model("User")
        client_model = self.get_model("Client")
        case_model = self.get_model("Case")
        damages_model = self.get_model("Damages")
        coverage_model = self.get_model("Coverage")
        user = self.create_user()

        payload = {
            "id": "call-123",
            "transcript": [
                {"speaker": "Agent", "text": "Tell me what happened."},
                {"speaker": "Caller", "text": "I was rear-ended at a stoplight."},
            ],
        }
        structured_output = {
            "client": {
                "name": "Jane Doe",
                "age": 42,
                "email": "jane@example.com",
                "phone": "555-0100",
                "liable": False,
                "liable_reason": "The other driver ran the red light.",
            },
            "incident": {"type": "Auto accident", "summary": "Rear-end collision."},
            "damages": {
                "treatment_received": True,
                "treatment_type": "Urgent care",
                "description": "Whiplash symptoms",
                "treatment_cost": "1250.50",
            },
            "coverage": {
                "type": "THIRD_PARTY",
                "policy_limit": "50000.00",
                "deductible": "1000.00",
                "insurer_name": "Carrier A",
            },
            "recommendation": {"decision": "REVIEW", "reason": "Needs further review."},
        }

        with patch("api.views.extract_structured_intake", return_value=structured_output) as extraction_mock:
            self.client.force_authenticate(user=user)
            response = self.client.post(
                "/api/intake-extract/",
                {"file": self.build_upload(payload)},
                format="multipart",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        extraction_mock.assert_called_once_with(payload)
        response_data = response.json()

        self.assertEqual(user_model.objects.count(), 1)
        self.assertEqual(client_model.objects.count(), 1)
        self.assertEqual(case_model.objects.count(), 1)
        self.assertEqual(damages_model.objects.count(), 1)
        self.assertEqual(coverage_model.objects.count(), 1)

        persisted_user = user_model.objects.get()
        client = client_model.objects.get()
        case = case_model.objects.get()
        damages = damages_model.objects.get()
        coverage = coverage_model.objects.get()

        self.assertEqual(response_data["case_id"], case.id)
        self.assertEqual(response_data["client_id"], client.id)
        self.assertEqual(response_data["damages_ids"], [damages.id])
        self.assertEqual(response_data["coverage_ids"], [coverage.id])
        self.assertEqual(response_data["structured_output"], structured_output)

        self.assertEqual(persisted_user.id, user.id)
        self.assertEqual(persisted_user.email, "sumanth@suits.com")
        self.assertEqual(case.user_id, user.id)
        self.assertEqual(case.client_id, client.id)
        self.assertEqual(case.incident_type, "Auto accident")
        self.assertEqual(case.incident_summary, "Rear-end collision.")
        self.assertEqual(case.recommendation, case_model.Recommendation.REVIEW)
        self.assertEqual(client.name, "Jane Doe")
        self.assertEqual(client.age, 42)
        self.assertEqual(client.email, "jane@example.com")
        self.assertEqual(client.phone, "555-0100")
        self.assertFalse(client.liable)
        self.assertEqual(client.liable_reason, "The other driver ran the red light.")
        self.assertTrue(damages.treatment_received)
        self.assertEqual(damages.treatment_type, "Urgent care")
        self.assertEqual(damages.description, "Whiplash symptoms")
        self.assertEqual(damages.treatment_cost, Decimal("1250.50"))
        self.assertEqual(coverage.type, coverage_model.CoverageType.THIRD_PARTY)
        self.assertEqual(coverage.policy_limit, Decimal("50000.00"))
        self.assertEqual(coverage.deductible, Decimal("1000.00"))
        self.assertEqual(coverage.insurer_name, "Carrier A")

    def test_post_reuses_authenticated_user_across_requests(self):
        user_model = self.get_model("User")
        user = self.create_user()

        payload = {
            "id": "call-123",
            "transcript": [{"speaker": "Caller", "text": "I was injured."}],
        }
        structured_output = {
            "client": {
                "name": "Jane Doe",
                "age": None,
                "email": None,
                "phone": None,
                "liable": None,
                "liable_reason": None,
            },
            "incident": {"type": "Auto accident", "summary": "Rear-end collision."},
            "damages": {
                "treatment_received": True,
                "treatment_type": None,
                "description": None,
                "treatment_cost": None,
            },
            "coverage": {"type": None, "policy_limit": None, "deductible": None, "insurer_name": None},
            "recommendation": {"decision": "REVIEW", "reason": "Needs further review."},
        }

        with patch("api.views.extract_structured_intake", return_value=structured_output):
            self.client.force_authenticate(user=user)
            first_response = self.client.post(
                "/api/intake-extract/",
                {"file": self.build_upload(payload)},
                format="multipart",
            )
            second_response = self.client.post(
                "/api/intake-extract/",
                {"file": self.build_upload(payload)},
                format="multipart",
            )

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(user_model.objects.count(), 1)

    def test_post_skips_empty_related_rows(self):
        client_model = self.get_model("Client")
        damages_model = self.get_model("Damages")
        coverage_model = self.get_model("Coverage")
        user = self.create_user()

        payload = {
            "id": "call-123",
            "transcript": [{"speaker": "Caller", "text": "I was injured."}],
        }
        structured_output = {
            "client": {
                "name": "Jane Doe",
                "age": None,
                "email": None,
                "phone": None,
                "liable": None,
                "liable_reason": None,
            },
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

        with patch("api.views.extract_structured_intake", return_value=structured_output):
            self.client.force_authenticate(user=user)
            response = self.client.post(
                "/api/intake-extract/",
                {"file": self.build_upload(payload)},
                format="multipart",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["damages_ids"], [])
        self.assertEqual(response.json()["coverage_ids"], [])
        self.assertEqual(damages_model.objects.count(), 0)
        self.assertEqual(coverage_model.objects.count(), 0)
        self.assertIsNone(client_model.objects.get().liable_reason)

    def test_post_rolls_back_records_if_persistence_fails(self):
        user_model = self.get_model("User")
        client_model = self.get_model("Client")
        case_model = self.get_model("Case")
        damages_model = self.get_model("Damages")
        coverage_model = self.get_model("Coverage")
        user = self.create_user()

        payload = {
            "id": "call-123",
            "transcript": [{"speaker": "Caller", "text": "I was injured."}],
        }
        structured_output = {
            "client": {"name": "Jane Doe", "age": None, "email": None, "phone": None, "liable": None},
            "incident": {"type": "Auto accident", "summary": "Rear-end collision."},
            "damages": {
                "treatment_received": True,
                "treatment_type": "Urgent care",
                "description": None,
                "treatment_cost": None,
            },
            "coverage": {
                "type": "THIRD_PARTY",
                "policy_limit": "50000.00",
                "deductible": None,
                "insurer_name": "Carrier A",
            },
            "recommendation": {"decision": "REVIEW", "reason": "Needs further review."},
        }

        with patch("api.views.extract_structured_intake", return_value=structured_output), patch(
            "api.views._create_coverage_record",
            side_effect=RuntimeError("db write failed"),
        ):
            self.client.force_authenticate(user=user)
            response = self.client.post(
                "/api/intake-extract/",
                {"file": self.build_upload(payload)},
                format="multipart",
            )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json(), {"detail": "Failed to persist extracted transcript data."})
        self.assertEqual(client_model.objects.count(), 0)
        self.assertEqual(case_model.objects.count(), 0)
        self.assertEqual(damages_model.objects.count(), 0)
        self.assertEqual(coverage_model.objects.count(), 0)
        self.assertEqual(user_model.objects.count(), 1)

    def test_post_requires_authentication(self):
        response = self.client.post(
            "/api/intake-extract/",
            {"file": self.build_upload({"id": "call-123", "transcript": []})},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_without_file_returns_bad_request(self):
        user = self.create_user()
        self.client.force_authenticate(user=user)

        response = self.client.post("/api/intake-extract/", {}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"detail": "A JSON file upload is required in the 'file' field."})

    def test_post_with_malformed_json_file_returns_bad_request(self):
        user = self.create_user()
        uploaded_file = SimpleUploadedFile(
            "transcript.json",
            b"{not valid json}",
            content_type="application/json",
        )

        self.client.force_authenticate(user=user)
        response = self.client.post("/api/intake-extract/", {"file": uploaded_file}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"detail": "Uploaded file did not contain valid JSON."})


class CaseReportApiTests(APITestCase):
    def get_model(self, model_name):
        try:
            return apps.get_model("api", model_name)
        except LookupError as exc:
            self.fail(f"Expected api.{model_name} model to exist: {exc}")

    def create_user(self, email):
        user_model = self.get_model("User")
        return user_model.objects.create_user(email=email, password="test-pass-123")

    def create_case(self, user, **case_overrides):
        client_model = self.get_model("Client")
        case_model = self.get_model("Case")

        client = client_model.objects.create(
            name="Jane Doe",
            age=42,
            email="jane@example.com",
            phone="555-0100",
            liable=False,
            liable_reason=case_overrides.pop("liable_reason", "The other driver ran the red light."),
        )
        reason = case_overrides.pop("recommendation_reason", "Needs further review.")
        case = case_model.objects.create(
            user=user,
            client=client,
            status=case_model.Status.ACTIVE,
            incident_type="Auto accident",
            incident_summary="Rear-end collision.",
            recommendation=case_model.Recommendation.REVIEW,
            recommendation_reason=reason,
            **case_overrides,
        )
        return case

    def test_get_returns_full_case_report_for_authenticated_owner(self):
        damages_model = self.get_model("Damages")
        coverage_model = self.get_model("Coverage")

        user = self.create_user("owner@example.com")
        case = self.create_case(user)
        damages_model.objects.create(
            case=case,
            treatment_received=True,
            treatment_type="Urgent care",
            description="Whiplash symptoms",
            treatment_cost=Decimal("1250.50"),
        )
        coverage_model.objects.create(
            case=case,
            type=coverage_model.CoverageType.THIRD_PARTY,
            insurer_name="Carrier A",
            policy_limit=Decimal("50000.00"),
            deductible=Decimal("1000.00"),
        )

        self.client.force_authenticate(user=user)
        response = self.client.get(f"/api/cases/{case.id}/report/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "case": {
                    "id": case.id,
                    "status": "ACTIVE",
                    "incident_type": "Auto accident",
                    "incident_summary": "Rear-end collision.",
                    "recommendation": "REVIEW",
                    "created_at": case.created_at.isoformat().replace("+00:00", "Z"),
                    "recommendation_reason": "Needs further review.",
                },
                "client": {
                    "name": "Jane Doe",
                    "age": 42,
                    "email": "jane@example.com",
                    "phone": "555-0100",
                    "liable": False,
                    "liable_reason": "The other driver ran the red light.",
                },
                "damages": {
                    "treatment_received": True,
                    "treatment_type": "Urgent care",
                    "description": "Whiplash symptoms",
                    "treatment_cost": "1250.50",
                },
                "coverage": {
                    "type": "THIRD_PARTY",
                    "insurer_name": "Carrier A",
                    "insurer_inferred": False,
                    "policy_limit": "50000.00",
                    "deductible": "1000.00",
                },
            },
        )

    def test_get_returns_null_blocks_when_related_records_are_missing(self):
        user = self.create_user("owner@example.com")
        case = self.create_case(user, liable_reason=None, recommendation_reason=None)

        self.client.force_authenticate(user=user)
        response = self.client.get(f"/api/cases/{case.id}/report/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.json()["case"]["recommendation_reason"])
        self.assertIsNone(response.json()["client"]["liable_reason"])
        self.assertIsNone(response.json()["damages"])
        self.assertIsNone(response.json()["coverage"])

    def test_get_uses_first_damages_and_coverage_records(self):
        damages_model = self.get_model("Damages")
        coverage_model = self.get_model("Coverage")

        user = self.create_user("owner@example.com")
        case = self.create_case(user)
        first_damages = damages_model.objects.create(
            case=case,
            treatment_received=True,
            treatment_type="Urgent care",
            description="First damages record",
            treatment_cost=Decimal("100.00"),
        )
        damages_model.objects.create(
            case=case,
            treatment_received=False,
            treatment_type="Physical therapy",
            description="Second damages record",
            treatment_cost=Decimal("200.00"),
        )
        first_coverage = coverage_model.objects.create(
            case=case,
            type=coverage_model.CoverageType.FIRST_PARTY,
            insurer_name="Carrier A",
            policy_limit=Decimal("1000.00"),
            deductible=Decimal("100.00"),
        )
        coverage_model.objects.create(
            case=case,
            type=coverage_model.CoverageType.THIRD_PARTY,
            insurer_name="Carrier B",
            policy_limit=Decimal("2000.00"),
            deductible=Decimal("200.00"),
        )

        self.client.force_authenticate(user=user)
        response = self.client.get(f"/api/cases/{case.id}/report/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["damages"]["description"], first_damages.description)
        self.assertEqual(response.json()["coverage"]["insurer_name"], first_coverage.insurer_name)
        self.assertFalse(response.json()["coverage"]["insurer_inferred"])

    def test_get_marks_sparse_persisted_coverage_as_inferred_for_demo_display(self):
        coverage_model = self.get_model("Coverage")

        user = self.create_user("owner@example.com")
        case = self.create_case(user)
        coverage_model.objects.create(
            case=case,
            insurer_name="Carrier A",
        )

        self.client.force_authenticate(user=user)
        response = self.client.get(f"/api/cases/{case.id}/report/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()["coverage"],
            {
                "type": None,
                "insurer_name": "Carrier A",
                "insurer_inferred": True,
                "policy_limit": None,
                "deductible": None,
            },
        )

    def test_get_accepts_bearer_token_authentication(self):
        user = self.create_user("owner@example.com")
        case = self.create_case(user)
        token = Token.objects.create(user=user)

        response = self.client.get(
            f"/api/cases/{case.id}/report/",
            HTTP_AUTHORIZATION=f"Bearer {token.key}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["case"]["id"], case.id)

    def test_get_returns_not_found_for_other_users_case(self):
        owner = self.create_user("owner@example.com")
        intruder = self.create_user("intruder@example.com")
        case = self.create_case(owner)

        self.client.force_authenticate(user=intruder)
        response = self.client.get(f"/api/cases/{case.id}/report/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_returns_not_found_for_missing_case(self):
        user = self.create_user("owner@example.com")

        self.client.force_authenticate(user=user)
        response = self.client.get("/api/cases/999999/report/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_requires_authentication(self):
        user = self.create_user("owner@example.com")
        case = self.create_case(user)

        response = self.client.get(f"/api/cases/{case.id}/report/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthTokenApiTests(APITestCase):
    def get_model(self, model_name):
        try:
            return apps.get_model("api", model_name)
        except LookupError as exc:
            self.fail(f"Expected api.{model_name} model to exist: {exc}")

    def test_post_returns_token_for_valid_email_and_password(self):
        user_model = self.get_model("User")
        user_model.objects.create_user(email="owner@example.com", password="test-pass-123")

        response = self.client.post(
            "/api/auth/token/",
            {"email": "owner@example.com", "password": "test-pass-123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.json())
        self.assertEqual(Token.objects.count(), 1)

    def test_post_reuses_existing_token_for_user(self):
        user_model = self.get_model("User")
        user = user_model.objects.create_user(email="owner@example.com", password="test-pass-123")
        token = Token.objects.create(user=user)

        response = self.client.post(
            "/api/auth/token/",
            {"email": "owner@example.com", "password": "test-pass-123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"token": token.key})
        self.assertEqual(Token.objects.count(), 1)

    def test_post_rejects_invalid_credentials(self):
        user_model = self.get_model("User")
        user_model.objects.create_user(email="owner@example.com", password="test-pass-123")

        response = self.client.post(
            "/api/auth/token/",
            {"email": "owner@example.com", "password": "wrong-pass"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"detail": "Invalid credentials."})
