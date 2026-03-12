import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_AllowedTopics = dict[int, set[int | None]]


def _load_allowed_topics(config_path: Path) -> _AllowedTopics:
    """Parse groups_config.json into a mapping of {group_id: {thread_id, ...}}.

    A group with no topics entries allows any thread (mapped to {None}).
    """
    with config_path.open() as f:
        data = json.load(f)

    allowed: _AllowedTopics = {}
    for group in data.get("allowed_groups", []):
        group_id: int = group["group_id"]
        topics: list[dict] = group.get("topics", [])
        if topics:
            allowed[group_id] = {t["thread_id"] for t in topics}
        else:
            allowed[group_id] = {None}
    return allowed


class AccessChecker:
    def __init__(self, config_path: Path) -> None:
        self._allowed = _load_allowed_topics(config_path)
        logger.info("Loaded access config: %d group(s)", len(self._allowed))

    def is_allowed(self, chat_id: int, thread_id: int | None) -> bool:
        """Return True if the chat_id/thread_id combination is permitted."""
        if chat_id not in self._allowed:
            return False
        allowed_threads = self._allowed[chat_id]
        return None in allowed_threads or thread_id in allowed_threads
