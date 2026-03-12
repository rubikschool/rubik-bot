import json
import logging
import os
from urllib.error import URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

METADATA_BASE_URL = "http://metadata.google.internal/computeMetadata/v1"
METADATA_HEADERS = {"Metadata-Flavor": "Google"}
METADATA_TIMEOUT_SECONDS = 3


def _fetch_metadata(path: str) -> str:
    req = Request(f"{METADATA_BASE_URL}/{path}", headers=METADATA_HEADERS)
    with urlopen(req, timeout=METADATA_TIMEOUT_SECONDS) as resp:
        return resp.read().decode()


def resolve_webhook_url() -> str | None:
    """Resolve webhook URL: manual override via WEBHOOK_URL env var, or auto-detect from Cloud Run metadata."""
    manual_url = os.getenv("WEBHOOK_URL")
    if manual_url:
        return manual_url.rstrip("/")

    try:
        project_id = _fetch_metadata("project/project-id")
        region_path = _fetch_metadata("instance/region")
        region = region_path.split("/")[-1]
        service_name = os.getenv("K_SERVICE")
        if not service_name:
            return None

        token = json.loads(
            _fetch_metadata("instance/service-accounts/default/token")
        )["access_token"]

        api_url = (
            f"https://run.googleapis.com/v2/projects/{project_id}"
            f"/locations/{region}/services/{service_name}"
        )
        req = Request(api_url, headers={"Authorization": f"Bearer {token}"})
        with urlopen(req, timeout=METADATA_TIMEOUT_SECONDS) as resp:
            return json.loads(resp.read().decode()).get("uri")
    except (URLError, KeyError, json.JSONDecodeError) as exc:
        logger.warning("Could not auto-detect Cloud Run service URL: %s", exc)
        return None
