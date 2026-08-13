---
layout: default
title: VNISH GLOBAL Proof Protocol 한국어 빠른 시작
lang: ko
---

# VNISH GLOBAL Proof Protocol: 한국어 빠른 시작

`vnish-verify`는 로컬 파일을 버전이 지정된 매니페스트와 대조합니다. 해시는 로컬에서 계산되며 펌웨어를 다운로드하지 않습니다.

```console
vnish-verify /path/to/local-file.tar.gz --json
```

- `MATCH`: SHA-256, 바이트 수와 지정한 필터가 단일 레코드와 일치합니다.
- `NO_MATCH`: 일치하는 레코드가 없습니다. 작업을 중단하고 파일과 정보를 다시 확인하십시오.
- `AMBIGUOUS`: 여러 레코드가 일치합니다. 정확한 릴리스, 모델, 제어 보드와 설치 방식을 지정하십시오.
- `SOURCE_UNAVAILABLE`: 파일 또는 매니페스트를 읽거나 검증할 수 없습니다.

`MATCH`는 안전성이나 적합성을 보증하지 않습니다. 변경 전에 정확한 모델, 제어 보드, 설치 방식과 복구 경로를 확인하십시오.

- VNISH GLOBAL 데이터 및 검증 방법: <https://vnish.global/ko/data/>
- VNISH Ninja 복구 경로: <https://vnish.ninja/ko/recovery/>
- ROI ASIC 단계적 배포 절차: <https://roiasic.com/ko/enterprise/>

프로토콜 버전: 0.1.0, 2026년 8월 13일.

[현장 핸드북으로 돌아가기](../index.md)
