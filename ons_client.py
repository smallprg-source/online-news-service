import json
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests


logger = logging.getLogger(__name__)


class OnlineNewsService:
    CATEGORIES = ("news", "notice", "event", "tips", "ads")

    def __init__(
        self,
        service_url: str,
        cache_dir: str | Path = "cache",
        timeout: int = 10,
    ) -> None:
        self.service_url = service_url
        self.cache_dir = Path(cache_dir)
        self.timeout = timeout
        self.service: dict[str, Any] = {}
        self.data: dict[str, list[dict[str, Any]]] = {
            category: [] for category in self.CATEGORIES
        }
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def load_service(self) -> dict[str, Any]:
        self.service = self._load_json(self.service_url, "service")
        return self.service

    def load_news(self) -> list[dict[str, Any]]:
        return self._load_category("news")

    def load_notice(self) -> list[dict[str, Any]]:
        return self._load_category("notice")

    def load_event(self) -> list[dict[str, Any]]:
        return self._load_category("event")

    def load_tips(self) -> list[dict[str, Any]]:
        return self._load_category("tips")

    def load_ads(self) -> list[dict[str, Any]]:
        return self._load_category("ads")

    def refresh(self) -> dict[str, list[dict[str, Any]]]:
        self.load_service()
        for category in self.CATEGORIES:
            self._load_category(category)
        return self.data

    def get_items(self, program_name: str) -> list[dict[str, Any]]:
        if not any(self.data.values()):
            self.refresh()

        now = date.today()
        result: list[dict[str, Any]] = []

        for category in self.CATEGORIES:
            for item in self.data.get(category, []):
                if self._matches_target(item, program_name) and self._is_active(item, now):
                    result.append(item)

        return sorted(result, key=lambda item: item.get("priority", 0), reverse=True)

    def _load_category(self, category: str) -> list[dict[str, Any]]:
        url = self._category_url(category)
        payload = self._load_json(url, category)
        items = payload.get("items", [])

        if not isinstance(items, list):
            logger.warning("%s latest.json has invalid items field", category)
            items = []

        self.data[category] = [
            item for item in items if isinstance(item, dict)
        ]
        return self.data[category]

    def _category_url(self, category: str) -> str:
        paths = self.service.get("paths", {})
        path = paths.get(category)
        if not path:
            logger.warning("service.json does not define path for %s", category)
            return ""
        return urljoin(self.service_url, path)

    def _load_json(self, url: str, cache_name: str) -> dict[str, Any]:
        if url:
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                payload = response.json()
                if isinstance(payload, dict):
                    self._write_cache(cache_name, payload)
                    return payload
                logger.warning("%s response is not a JSON object", cache_name)
            except requests.RequestException as exc:
                logger.warning("failed to download %s: %s", cache_name, exc)
            except ValueError as exc:
                logger.warning("failed to parse %s JSON: %s", cache_name, exc)

        cached = self._read_cache(cache_name)
        if cached is not None:
            return cached

        logger.warning("cache for %s is not available", cache_name)
        return {}

    def _cache_path(self, cache_name: str) -> Path:
        safe_name = "".join(
            char if char.isalnum() or char in ("-", "_") else "_"
            for char in cache_name
        )
        return self.cache_dir / f"{safe_name}.json"

    def _write_cache(self, cache_name: str, payload: dict[str, Any]) -> None:
        path = self._cache_path(cache_name)
        try:
            path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError as exc:
            logger.warning("failed to write cache %s: %s", path, exc)

    def _read_cache(self, cache_name: str) -> dict[str, Any] | None:
        path = self._cache_path(cache_name)
        try:
            with path.open("r", encoding="utf-8") as file:
                payload = json.load(file)
            if isinstance(payload, dict):
                logger.info("loaded %s from cache", cache_name)
                return payload
            logger.warning("cache %s is not a JSON object", path)
        except FileNotFoundError:
            return None
        except (OSError, ValueError) as exc:
            logger.warning("failed to read cache %s: %s", path, exc)
        return None

    @staticmethod
    def _matches_target(item: dict[str, Any], program_name: str) -> bool:
        target = item.get("target", ["*"])
        if not isinstance(target, list):
            return False
        return "*" in target or program_name in target

    @staticmethod
    def _is_active(item: dict[str, Any], today: date) -> bool:
        start = OnlineNewsService._parse_date(item.get("start"))
        end = OnlineNewsService._parse_date(item.get("end"))
        if start and today < start:
            return False
        if end and today > end:
            return False
        return True

    @staticmethod
    def _parse_date(value: Any) -> date | None:
        if not value:
            return None
        if isinstance(value, date):
            return value
        if not isinstance(value, str):
            return None
        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                logger.warning("invalid date value: %s", value)
                return None
