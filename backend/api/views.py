from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Case, CaseLog
from .serializers import (
    CaseCreateSerializer,
    CaseDetailSerializer,
    CaseListSerializer,
    CaseStageAdvanceSerializer,
)


@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok"})


class CaseListCreateView(APIView):
    def get(self, request):
        queryset = Case.objects.select_related("client", "user").all().order_by("case_id")

        status_filter = request.query_params.get("status")
        stage_filter = request.query_params.get("stage")

        print(
            "[CaseListCreateView.get] Listing cases with "
            f"status={status_filter!r}, stage={stage_filter!r}."
        )

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if stage_filter:
            queryset = queryset.filter(stage=stage_filter)

        serializer = CaseListSerializer(queryset, many=True)
        print(
            "[CaseListCreateView.get] Returning "
            f"{len(serializer.data)} cases after filtering."
        )
        return Response(serializer.data)

    def post(self, request):
        print(
            "[CaseListCreateView.post] Received case intake payload for "
            f"{request.data.get('client_email')!r}."
        )
        serializer = CaseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        case = serializer.save()
        print(
            "[CaseListCreateView.post] Case created successfully with "
            f"case_id={case.case_id}."
        )
        return Response(CaseDetailSerializer(case).data, status=status.HTTP_201_CREATED)


class CaseDetailView(RetrieveAPIView):
    queryset = Case.objects.select_related("client", "user").prefetch_related("logs")
    serializer_class = CaseDetailSerializer
    lookup_field = "case_id"


class CaseStageAdvanceView(APIView):
    def patch(self, request, case_id):
        print(f"[CaseStageAdvanceView.patch] Advancing case {case_id}.")
        case = get_object_or_404(Case, case_id=case_id)
        serializer = CaseStageAdvanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        next_stage = case.get_next_stage()
        if next_stage is None:
            print(
                "[CaseStageAdvanceView.patch] Case is already at the final stage "
                f"for case_id={case_id}."
            )
            return Response(
                {"detail": "Case is already at the final stage."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        case.stage = next_stage
        case.save(update_fields=["stage"])

        description = serializer.validated_data.get(
            "description",
            f"Case advanced to {case.get_stage_display()}.",
        )
        log = CaseLog.objects.create(
            case=case,
            stage=next_stage,
            description=description,
        )

        print(
            "[CaseStageAdvanceView.patch] Advanced case "
            f"{case_id} to {next_stage} and created log {log.log_id}."
        )

        return Response(
            {
                "case_id": case.case_id,
                "stage": case.stage,
                "log": {
                    "log_id": log.log_id,
                    "timestamp": log.timestamp,
                    "stage": log.stage,
                    "description": log.description,
                },
            }
        )
