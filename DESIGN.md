# Kumiho Design Language

kumiho.io 프로덕션 CSS에서 추출한 브랜드 토큰과, 이를 적용한 보고서/문서 템플릿 규격.
빌드 산출물(Tailwind)에서 실사용 값만 검증해 기록했다 — 추측 값 없음.

> 적용 대상: 기술 보고서 · 벤치마크 리포트 · 비교 분석 · 아티팩트 HTML 문서.
> 제품 UI는 kumiho.io / 각 앱의 자체 스타일시트가 우선한다.

---

## 1. 브랜드 컬러 토큰 (kumiho.io 검증값)

### Ground — 다크 커밋

| 토큰 | 값 | 용도 |
|---|---|---|
| `ink` | `#0C0C0E` | 페이지 배경 (근흑) |
| `surface` | `#131316` | 패널·카드 배경 |
| `deep-navy` | `#0F1629` | 그라디언트 종점, 보조 심도 |
| 보더 | `rgba(255,255,255,0.10)` | 패널 1px 보더 (white/10) |
| 보더-약 | `rgba(255,255,255,0.05)` | 헤어라인, 행 구분 |

### Fox — 브랜드 액센트 스케일

| 토큰 | 값 | 용도 |
|---|---|---|
| `fox-100` | `#FDE3DD` | 액센트 위 텍스트(밝음) |
| `fox-200` | `#FCC3B7` | 보조 하이라이트 |
| `fox-300` | `#FA9A85` | 링크 호버, 인용 강조 |
| `fox-400` | `#F36C4C` | 링·보더 액센트, 아이브로 |
| `fox-500` | `#EF4C28` | 주 액센트 (CTA·도트·핵심 강조) |
| `coral` | `#FF8C6B` | 그라디언트 밝은 끝 |

- 액센트 그라디언트: `fox-500 → coral` (바 차트·히어로 글로우)
- 글로우 섀도: `0 0 80px -24px rgba(239,76,40,0.5)`
- 틴트 배경: `fox-400/10`~`/20` (액센트 배지·호버)

### 보조 팔레트 (그라디언트 파트너 — 사이트 실사용)

| 계열 | 값 | 보고서 내 역할 |
|---|---|---|
| amber | `#FBBF24` / `#FCD34D` | 다이어그램 패밀리 ① (단기/버퍼) |
| purple | `#A855F7` / `#9333EA` | 다이어그램 패밀리 ② (그래프/서버 계약) |
| lime | `#BEF264` | 다이어그램 패밀리 ③ (로컬/정책/긍정) |
| cyan | `#67E8F9` | 보조 정보 축 |
| red | `#EF4444` | 경계·리스크·회귀 (음수는 숨기지 않고 이 색으로 노출) |

### 시맨틱 (보고서용 파생)

| 역할 | 값 |
|---|---|
| good / 검증됨 | `lime #BEF264` (틴트 12%) |
| warn / 단서 | `amber #FBBF24` (틴트 14%) |
| critical / 회귀 | `red #EF4444` |
| muted 텍스트 | `#9CA3AF` 계열 (white 60~65%) |
| 본문 텍스트 | `#E7E5E4` 계열 (warm near-white) |

## 2. 타이포그래피

| 역할 | 스택 | 비고 |
|---|---|---|
| 본문 (sans) | `Inter, Pretendard, "Apple SD Gothic Neo", "Malgun Gothic", "Segoe UI", sans-serif` | 사이트 본문 = Inter. 한글은 Pretendard/시스템 폴백 |
| 코드·데이터 (mono) | `"JetBrains Mono", "Cascadia Code", Consolas, "D2Coding", monospace` | 사이트 코드 = JetBrains Mono. 수치엔 `tabular-nums` |
| 보고서 디스플레이 (serif) | `"Nanum Myeongjo", "Noto Serif KR", Batang, serif` | 보고서 대제목·판결 인용 전용 (사이트 UI엔 없음 — 보고서 확장) |

- 아이브로: mono · uppercase · `letter-spacing 0.2em` · `fox-400`
- 대제목: 명조 · 서술형 문장 ("쓰기 측은 성숙, 읽기 측이 못 따라간다")
- 아티팩트/오프라인 환경은 외부 폰트 로드 불가 → 위 스택의 시스템 폴백에 의존 (웹폰트 URL 링크 금지)

## 3. 보고서 템플릿 문법

모든 도표·데이터는 **패널** 안에 산다:

```
┌ 패널 헤더바 ─ ● 도트(fox-500) + 모노 대문자 제목        우측: 뮤트 메타 ┐
│ 본문 (다이어그램 / 차트 / 카드 그리드)                                  │
└ 푸터 스트립 ─ 모노 파인프린트: 범례 · 단서 · 측정 조건                  ┘
```

- **섹션**: `01 — SECTION NAME` 아이브로 → 명조 대제목 → 리드 문단(≤3줄)
- **다이어그램**: 패밀리색 1px 보더 + 8% 틴트 노드 카드(제목 + 모노 서브라벨), 점선 그룹 컨테이너 + 떠있는 라벨, 라벨 달린 얇은 화살표, 푸터 색 범례
- **바 차트**: 수평 그라디언트 바(`fox-500→coral`; 회귀는 red), 우측 tabular-nums 수치 + 델타 주석(`+0.107 #1`), 종합 행 볼드, 조건은 푸터 파인프린트
- **타임라인 스트립**: 수평선 + 도트, 위 버전·제목 / 아래 모노 근거 한 줄
- **head-to-head**: 좌우 2패널("X가 앞서는 것" + 뮤트 부제), 행마다 헤어라인
- **우선순위 카드**: 좌측 세로 스트라이프 = 심각도 (P0 `red` / P1 `amber` / P2 `cyan` / P3 뮤트)
- **판결**: "계속 지킬 것"/"직설적으로" 2열(모노 넘버링) + 전폭 인용 패널(명조 이탤릭, 핵심 구절만 fox-300) + 모노 서명 `— 이름 · 날짜 · 방법`
- **푸터**: 모노 라벨-값 메타 스트립 (분석 대상 / 방법 / 검증 / 원문)
- **정직성 = 디자인 요소**: 회귀·미검증·단서는 본문 안에 red/파인프린트로 배치. 숨기지 않는다.

콘텐츠 규칙(별개): 기능/역량 문서는 현재-상태만 서술 — 변경 이력·PR 번호·"~웨이브에서 반영" 서사 금지. 측정 날짜·조건은 재현 조건이므로 유지.

## 4. 시작용 토큰 블록 (HTML 아티팩트)

```css
:root {
  --ink: #0C0C0E; --surface: #131316; --deep: #0F1629;
  --line: rgba(255,255,255,0.10); --hairline: rgba(255,255,255,0.05);
  --text: #E7E5E4; --muted: #9CA3AF;
  --fox: #EF4C28; --fox-hi: #F36C4C; --fox-soft: #FA9A85; --coral: #FF8C6B;
  --fam-a: #FBBF24; /* 단기 */  --fam-b: #A855F7; /* 그래프 */
  --fam-c: #BEF264; /* 로컬/정책 */  --fam-d: #EF4444; /* 경계/회귀 */
  --sans: Inter, Pretendard, "Apple SD Gothic Neo", "Malgun Gothic", "Segoe UI", sans-serif;
  --mono: "JetBrains Mono", "Cascadia Code", Consolas, "D2Coding", monospace;
  --serif: "Nanum Myeongjo", "Noto Serif KR", Batang, serif;
}
/* 노드 카드: border: 1px solid color-mix(in srgb, var(--fam-x) 55%, transparent);
   배경: color-mix(in srgb, var(--fam-x) 8%, var(--surface)) */
```

보고서는 다크 단일 테마로 커밋한다 (브랜드 그라운드가 다크). 라이트 변형이 필요한 문서는 이 파일의 토큰을 명도 반전이 아니라 별도 정의로 만든다.
