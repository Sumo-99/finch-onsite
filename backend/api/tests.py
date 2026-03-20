from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Case, CaseLog, Client, User


class CaseApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="owner@example.com",
            password="password123",
        )
        self.client_record = Client.objects.create(
            name="Alex Smith",
            email="alex@example.com",
            phone_number="5551234567",
        )
        self.case = Case.objects.create(
            start_date="2026-03-19",
            intake_date="2026-03-18",
            incident_type="Auto accident",
            insurance_company_name="Acme Insurance",
            status=Case.Status.ACTIVE,
            stage=Case.Stage.INTAKE,
            client=self.client_record,
            user=self.user,
        )

    def test_create_case_uses_ui_payload_and_defaults(self):
        response = self.client.post(
            reverse("case-list-create"),
            {
                "client_name": "Jordan Lee",
                "client_email": "jordan@example.com",
                "incident_date": "2026-03-18",
                "incident_type": "Slip and fall",
                "insurance_company_name": "Beacon Mutual",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        case = Case.objects.latest("case_id")
        self.assertEqual(Case.objects.count(), 2)
        self.assertEqual(case.client.email, "jordan@example.com")
        self.assertEqual(case.client.name, "Jordan Lee")
        self.assertEqual(case.user, self.user)
        self.assertEqual(case.status, Case.Status.ACTIVE)
        self.assertEqual(case.stage, Case.Stage.INTAKE)
        self.assertEqual(case.intake_date.isoformat(), "2026-03-18")
        self.assertEqual(case.start_date, timezone.localdate())
        self.assertEqual(response.data["case_id"], case.case_id)

    def test_create_case_reuses_existing_client_by_email(self):
        response = self.client.post(
            reverse("case-list-create"),
            {
                "client_name": "Alexandra Smith",
                "client_email": self.client_record.email,
                "incident_date": "2026-03-18",
                "incident_type": "Slip and fall",
                "insurance_company_name": "Beacon Mutual",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        case = Case.objects.latest("case_id")
        self.assertEqual(case.client_id, self.client_record.client_id)
        self.assertEqual(Client.objects.count(), 1)

    def test_list_cases_with_filters(self):
        closed_case = Case.objects.create(
            start_date="2026-03-21",
            intake_date="2026-03-20",
            incident_type="Property damage",
            insurance_company_name="Beacon Mutual",
            status=Case.Status.CLOSED,
            stage=Case.Stage.MMI_REACHED,
            client=self.client_record,
            user=self.user,
        )

        response = self.client.get(
            reverse("case-list-create"),
            {"status": "closed", "stage": "MMI_reached"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["case_id"], closed_case.case_id)

    def test_case_detail_includes_logs(self):
        log = CaseLog.objects.create(
            case=self.case,
            stage=Case.Stage.INTAKE,
            description="Case opened.",
        )

        response = self.client.get(
            reverse("case-detail", kwargs={"case_id": self.case.case_id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["logs"]), 1)
        self.assertEqual(response.data["logs"][0]["log_id"], log.log_id)

    def test_advance_stage_creates_case_log(self):
        response = self.client.patch(
            reverse("case-stage-advance", kwargs={"case_id": self.case.case_id}),
            {"description": "Letter of representation sent."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.case.refresh_from_db()
        self.assertEqual(self.case.stage, Case.Stage.LOR)
        self.assertEqual(self.case.logs.count(), 1)
        self.assertEqual(self.case.logs.first().description, "Letter of representation sent.")

    def test_advance_stage_rejects_final_stage(self):
        self.case.stage = Case.Stage.DEMAND_PAGE_GENERATED
        self.case.save(update_fields=["stage"])

        response = self.client.patch(
            reverse("case-stage-advance", kwargs={"case_id": self.case.case_id}),
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
