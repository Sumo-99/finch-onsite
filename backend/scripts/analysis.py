import argparse
import json
import logging
import os
from pathlib import Path
import sys
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

DEFAULT_MODEL = os.getenv("OPENAI_INTAKE_MODEL", "gpt-4.1-mini")
DEFAULT_INCIDENT_SUMMARY = "No clear incident summary was provided."
DEFAULT_RECOMMENDATION_REASON = "Insufficient information was provided for a stronger recommendation."
ALLOWED_RECOMMENDATIONS = {"ACCEPT", "REJECT", "REVIEW"}

LEGAL_INTAKE_PROMPT = """
You are a legal intake extraction assistant.

Review the provided intake transcript and return only JSON that matches this shape:
{
  "client": {
    "name": string | null,
    "age": integer | null,
    "email": string | null,
    "phone": string | null,
    "liable": boolean | null,
    "liable_reason": string | null
    // Infer from the incident description who caused the incident.
    // Set to false if another party clearly caused the harm 
    // (e.g. another driver, a property owner, an employer, an animal owner).
    // Set to true only if the client's own actions caused or contributed to the incident.
    // Set to null only if genuinely cannot be determined from the transcript.
    // Set liable_reason only when the transcript includes specific facts that directly
    // support the liable assessment; otherwise set it to null.
  },
  "incident": {
    "type": string | null,
    "summary": string
  },
  "damages": {
    "treatment_received": boolean,
    "treatment_type": string | null,
    "description": string | null,
    "treatment_cost": string | null
  },
  "coverage": {
    "type": string | null,
    "policy_limit": string | null,
    "deductible": string | null,
    "insurer_name": string | null,
    "insurer_inferred": boolean
  },
  "recommendation": {
    "decision": "ACCEPT" | "REJECT" | "REVIEW",
    "reason": string
  }
}

Extraction rules:
- Use null when the transcript does not support a field.
- Use false only for damages.treatment_received when treatment is not stated or is unclear.
- Set insurer_name only when the caller explicitly states the name of an insurance company (e.g. "my insurance is Progressive", "Allstate is his carrier"). Do not set it from vague references like "my health insurance" or "marketplace coverage" — those are not named insurers.
- Set insurer_inferred to true if insurer_name was implied, described generically, or inferred from context rather than explicitly named.
- Set insurer_inferred to false if insurer_name was explicitly stated by the caller.
- Set insurer_inferred to false if insurer_name is null.
- Use these rules in order to determine recommendation.decision:
  ACCEPT if all three of the following are true:
    - liable is false (another party clearly caused the harm)
    - damages.treatment_received is true
    - damages.treatment_cost is non-null OR damages.description contains credible injury detail
  REJECT if any of the following are true:
    - liable is true (the client caused or contributed to the incident)
    - damages.treatment_received is false and description is null
    - there is a clear disqualifying factor stated in the transcript (e.g. client explicitly does not want to pursue, statute of limitations has clearly passed, no actionable harm described)
  REVIEW in all other cases, including:
    - liable is null
    - liability is ambiguous or contested
    - treatment was received but coverage and cost are both null
    - key information is missing that prevents a confident determination
  Always apply REJECT before ACCEPT. If both conditions appear to be met, prefer REJECT. When in doubt, use REVIEW over ACCEPT.
- liable_reason must cite specific facts from the transcript to justify the liable determination. Do not write generic statements like 'another party was at fault'. Reference concrete evidence from the call. Example: 'The City of Denver is responsible for maintaining the sidewalk where the incident occurred. The city placed cones three days after the incident, indicating prior awareness of the hazard.'
- Do not invent specific facts.
- Return JSON only. No markdown, no prose, no code fences.
""".strip()

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


class ClientExtraction(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str | None = None
    age: int | None = None
    email: str | None = None
    phone: str | None = None
    liable: bool | None = None
    liable_reason: str | None = None


class IncidentExtraction(BaseModel):
    model_config = ConfigDict(extra="ignore")

    type: str | None = None
    summary: str | None = None


class DamagesExtraction(BaseModel):
    model_config = ConfigDict(extra="ignore")

    treatment_received: bool | None = None
    treatment_type: str | None = None
    description: str | None = None
    treatment_cost: str | None = None


class CoverageExtraction(BaseModel):
    model_config = ConfigDict(extra="ignore")

    type: str | None = None
    policy_limit: str | None = None
    deductible: str | None = None
    insurer_name: str | None = None
    insurer_inferred: bool = False


class RecommendationExtraction(BaseModel):
    model_config = ConfigDict(extra="ignore")

    decision: str | None = None
    reason: str | None = None


class IntakeExtraction(BaseModel):
    model_config = ConfigDict(extra="ignore")

    client: ClientExtraction | None = None
    incident: IncidentExtraction | None = None
    damages: DamagesExtraction | None = None
    coverage: CoverageExtraction | None = None
    recommendation: RecommendationExtraction | None = None


def extract_structured_intake(payload: dict[str, Any]) -> dict[str, Any]:
    normalized_payload = _validate_payload(payload)
    rendered_transcript = _render_transcript(normalized_payload["transcript"])

    logger.info(
        "Starting intake extraction for payload id=%s with %s transcript turns.",
        normalized_payload.get("id") or "unknown",
        len(normalized_payload["transcript"]),
    )

    raw_output = _request_structured_output(
        payload_id=normalized_payload.get("id"),
        rendered_transcript=rendered_transcript,
    )
    normalized_output = _normalize_structured_output(raw_output)

    logger.info(
        "Finished intake extraction for payload id=%s with recommendation=%s.",
        normalized_payload.get("id") or "unknown",
        normalized_output["recommendation"]["decision"],
    )
    return normalized_output


def _validate_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary.")

    transcript = payload.get("transcript")
    if not isinstance(transcript, list):
        raise ValueError("Payload must include a transcript list.")

    return payload


def _render_transcript(transcript: list[Any]) -> str:
    lines: list[str] = []

    for turn in transcript:
        if not isinstance(turn, dict):
            continue

        text = _normalize_string(turn.get("text"))
        if text is None:
            continue

        speaker = _normalize_string(turn.get("speaker")) or "Unknown"
        lines.append(f"{speaker}: {text}")

    return "\n".join(lines)


def _request_structured_output(payload_id: Any, rendered_transcript: str) -> dict[str, Any]:
    logger.info("Preparing OpenAI extraction request for payload id=%s.", payload_id or "unknown")

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    user_prompt = _build_user_prompt(payload_id=payload_id, rendered_transcript=rendered_transcript)

    try:
        completion = client.chat.completions.parse(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": LEGAL_INTAKE_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format=IntakeExtraction,
        )
    except Exception:
        logger.exception("OpenAI extraction request failed for payload id=%s.", payload_id or "unknown")
        raise

    message = completion.choices[0].message

    if getattr(message, "parsed", None):
        logger.info("OpenAI extraction request completed with typed parsing.")
        return message.parsed.model_dump()

    refusal = getattr(message, "refusal", None)
    if refusal:
        logger.error("OpenAI extraction refused the request: %s", refusal)
        raise ValueError(f"OpenAI extraction refused the request: {refusal}")

    raw_content = _extract_message_content(message)
    logger.info("OpenAI extraction returned unparsed content; falling back to JSON decoding.")
    return _parse_json_output(raw_content)


def _build_user_prompt(payload_id: Any, rendered_transcript: str) -> str:
    transcript_block = rendered_transcript or "No non-empty transcript turns were provided."
    return (
        f"Payload ID: {payload_id or 'unknown'}\n"
        "Extract the legal intake information from this transcript.\n\n"
        f"{transcript_block}"
    )


def _extract_message_content(message: Any) -> str:
    content = getattr(message, "content", None)

    if isinstance(content, str):
        return content.strip()

    if not isinstance(content, list):
        raise ValueError("OpenAI response did not include parseable content.")

    parts: list[str] = []
    for item in content:
        if isinstance(item, dict):
            text = item.get("text")
            if isinstance(text, str):
                parts.append(text)
            continue

        text = getattr(item, "text", None)
        if isinstance(text, str):
            parts.append(text)

    combined = "".join(parts).strip()
    if not combined:
        raise ValueError("OpenAI response content was empty.")
    return combined


def _parse_json_output(raw_content: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        raise ValueError("OpenAI response did not contain valid JSON.") from exc

    if not isinstance(parsed, dict):
        raise ValueError("OpenAI response JSON must be an object.")

    return parsed


def _normalize_structured_output(raw_output: Any) -> dict[str, Any]:
    output = raw_output if isinstance(raw_output, dict) else {}

    client = output.get("client") if isinstance(output.get("client"), dict) else {}
    incident = output.get("incident") if isinstance(output.get("incident"), dict) else {}
    damages = output.get("damages") if isinstance(output.get("damages"), dict) else {}
    coverage = output.get("coverage") if isinstance(output.get("coverage"), dict) else {}
    recommendation = output.get("recommendation") if isinstance(output.get("recommendation"), dict) else {}
    normalized_insurer_name = _normalize_string(coverage.get("insurer_name"))
    normalized_insurer_inferred = _normalize_boolean(
        coverage.get("insurer_inferred"),
        default=False,
    )
    if normalized_insurer_name is None:
        normalized_insurer_inferred = False

    return {
        "client": {
            "name": _normalize_string(client.get("name")),
            "age": _normalize_integer(client.get("age")),
            "email": _normalize_string(client.get("email")),
            "phone": _normalize_string(client.get("phone")),
            "liable": _normalize_boolean(client.get("liable")),
            "liable_reason": _normalize_string(client.get("liable_reason")),
        },
        "incident": {
            "type": _normalize_string(incident.get("type")),
            "summary": _normalize_non_empty_string(
                incident.get("summary"),
                fallback=DEFAULT_INCIDENT_SUMMARY,
            ),
        },
        "damages": {
            "treatment_received": _normalize_boolean(damages.get("treatment_received"), default=False),
            "treatment_type": _normalize_string(damages.get("treatment_type")),
            "description": _normalize_string(damages.get("description")),
            "treatment_cost": _normalize_numeric_string(damages.get("treatment_cost")),
        },
        "coverage": {
            "type": _normalize_string(coverage.get("type")),
            "policy_limit": _normalize_numeric_string(coverage.get("policy_limit")),
            "deductible": _normalize_numeric_string(coverage.get("deductible")),
            "insurer_name": normalized_insurer_name,
            "insurer_inferred": normalized_insurer_inferred,
        },
        "recommendation": {
            "decision": _normalize_recommendation_decision(recommendation.get("decision")),
            "reason": _normalize_non_empty_string(
                recommendation.get("reason"),
                fallback=DEFAULT_RECOMMENDATION_REASON,
            ),
        },
    }


def _normalize_string(value: Any) -> str | None:
    if value is None:
        return None

    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)

    return None


def _normalize_non_empty_string(value: Any, fallback: str) -> str:
    return _normalize_string(value) or fallback


def _normalize_integer(value: Any) -> int | None:
    if isinstance(value, bool) or value is None:
        return None

    if isinstance(value, int):
        return value

    if isinstance(value, float) and value.is_integer():
        return int(value)

    if isinstance(value, str):
        normalized = value.strip()
        if normalized.isdigit():
            return int(normalized)

    return None


def _normalize_boolean(value: Any, default: bool | None = None) -> bool | None:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "y", "1"}:
            return True
        if normalized in {"false", "no", "n", "0"}:
            return False

    return default


def _normalize_numeric_string(value: Any) -> str | None:
    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return str(value)

    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return None


def _normalize_recommendation_decision(value: Any) -> str:
    normalized = _normalize_string(value)
    if normalized is None:
        return "REVIEW"

    decision = normalized.upper()
    if decision in ALLOWED_RECOMMENDATIONS:
        return decision

    return "REVIEW"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract structured intake data from a transcript JSON file.",
    )
    parser.add_argument(
        "input_file",
        help="Path to a JSON file with the intake payload.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Optional path to write the extracted JSON output.",
    )
    return parser.parse_args()


def _load_payload_from_file(input_file: str) -> dict[str, Any]:
    with open(input_file, encoding="utf-8") as file_handle:
        payload = json.load(file_handle)

    if not isinstance(payload, dict):
        raise ValueError("Input file JSON must contain a top-level object.")

    return payload


def main() -> int:
    args = _parse_args()
    result = extract_structured_intake(_load_payload_from_file(args.input_file))
    serialized = json.dumps(result, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as file_handle:
            file_handle.write(f"{serialized}\n")
        logger.info("Wrote extracted intake JSON to %s.", args.output)
        return 0

    print(serialized)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        logger.exception("CLI execution failed: %s", exc)
        raise SystemExit(1)
