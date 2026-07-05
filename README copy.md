PhotoBoard뿐 아니라 다른 프로그램에서도 사용할 수 있는 범용 Online News Service를 개발하려고 합니다.

다음 요구사항에 맞는 프로젝트를 설계하고 구현해 주세요.

==========================
프로젝트명
==========================

Online News Service

==========================
목적
==========================

GitHub Repository를 서버처럼 사용하여
여러 프로그램에서 인터넷을 통해

- 뉴스
- 공지사항
- 이벤트
- 팁
- 광고
- 업데이트 정보

등을 받아 표시할 수 있는 범용 서비스입니다.

REST API 서버는 사용하지 않습니다.

GitHub Raw JSON만 사용합니다.

==========================
Repository 구조
==========================

online-news-service

README.md

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

==========================
service.json
==========================

service.json은
모든 JSON 위치와 설정을 관리하는 중심 파일입니다.

예)

- refresh_minutes
- news path
- notice path
- event path
- tips path
- ads path

등을 포함합니다.

프로그램은
service.json만 알고 있어야 합니다.

==========================
latest.json 공통 규격
==========================

모든 latest.json은 동일한 구조를 사용합니다.

items 배열을 갖습니다.

각 item은

id
title
summary
url
icon
type
priority
start
end
target

을 포함합니다.

target은

["*"]

이면 모든 프로그램

["PhotoBoard"]

이면 PhotoBoard만 표시됩니다.

==========================
Python 라이브러리
==========================

requests

==========================
Python 모듈
==========================

ons_client.py

클래스

OnlineNewsService

메소드

load_service()

load_news()

load_notice()

load_event()

load_tips()

load_ads()

refresh()

get_items(program_name)

를 구현합니다.

==========================
동작
==========================

1.
service.json 다운로드

2.
service.json을 이용하여

news

notice

event

tips

ads

를 다운로드

3.
JSON 파싱

4.
메모리에 저장

5.
target을 검사하여

프로그램에 맞는 item만 반환

==========================
예외처리
==========================

GitHub 연결 실패

↓

마지막 캐시 사용

↓

캐시도 없으면 빈 리스트 반환

==========================
캐시
==========================

cache 폴더에 저장

다음 실행 시 사용

==========================
로그
==========================

logging 모듈 사용
