import json
import os
import tempfile

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from scripts.analysis import extract_structured_intake


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


@api_view(["POST"])
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
        return Response(
            {"detail": "Failed to process uploaded transcript."},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    finally:
        _delete_temp_file(temp_file_path)

    return Response(structured_output, status=status.HTTP_200_OK)
