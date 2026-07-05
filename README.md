# Online News Service

GitHub Repository를 서버처럼 사용하여 여러 프로그램에서 뉴스, 공지사항, 이벤트, 팁, 광고, 업데이트 정보를 받아 표시할 수 있는 범용 온라인 공지 서비스입니다.

REST API 서버 없이 GitHub Raw JSON 파일만 사용합니다.

## Repository 구조

```text
online-news-service/
  README.md
  ons_client.py
  config/
    service.json
  news/
    latest.json
  notice/
    latest.json
  event/
    latest.json
  tips/
    latest.json
  ads/
    latest.json
  archive/
  cache/
```

## 사용 방법

프로그램은 `config/service.json`의 GitHub Raw URL만 알고 있으면 됩니다.

```python
from ons_client import OnlineNewsService

service_url = "https://raw.githubusercontent.com/USER/online-news-service/main/config/service.json"

ons = OnlineNewsService(service_url)
ons.refresh()

items = ons.get_items("PhotoBoard")
for item in items:
    print(item["title"])
```

## JSON 규격

모든 `latest.json`은 같은 구조를 사용합니다.

```json
{
  "version": 1,
  "updated": "2026-07-05T17:00:00+09:00",
  "items": [
    {
      "id": "news-20260705-001",
      "title": "제목",
      "summary": "요약",
      "url": "https://example.com",
      "icon": "news",
      "type": "news",
      "priority": 10,
      "start": "2026-07-05",
      "end": "2026-07-31",
      "target": ["*"]
    }
  ]
}
```

`target`이 `["*"]`이면 모든 프로그램에 표시되고, `["PhotoBoard"]`이면 PhotoBoard에만 표시됩니다.

## 예외 처리

GitHub 연결 또는 JSON 파싱에 실패하면 마지막 캐시를 사용합니다. 캐시도 없으면 빈 리스트를 반환합니다.

## 의존성

```text
requests
```
