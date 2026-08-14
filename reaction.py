import time
import random
import streamlit as st

# 1. 페이지 기본 설정 (타이틀, 레이아웃, 아이콘)
st.set_page_config(
    page_title="⚡ 반응속도 테스트",
    page_icon="⚡",
    layout="centered"
)

# 2. 세션 상태(Session State) 초기화
# 상태 종류: "READY" (대기), "WAITING" (초록색 기다리는 중), "CLICK" (초록색 바뀜/클릭), "TOO_EARLY" (성급함)
if "state" not in st.session_state:
    st.session_state.state = "READY"
if "start_time" not in st.session_state:
    st.session_state.start_time = 0
if "reaction_time" not in st.session_state:
    st.session_state.reaction_time = None
if "history" not in st.session_state:
    st.session_state.history = []  # 측정 기록 저장용 리스트


# 3. 다크 테마 기반 반응형 CSS 스타일
st.markdown("""
    <style>
    .stApp {
        background-color: #121218;
        color: #ffffff;
    }
    
    /* 화면 크기에 맞춰 반응하는 타이틀 및 안내문구 */
    .title-text {
        text-align: center;
        font-size: clamp(2rem, 6vw, 3rem);
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .desc-text {
        text-align: center;
        color: #a0a0b0;
        font-size: clamp(1rem, 3vw, 1.2rem);
        margin-bottom: 1.5rem;
    }

    /* 기록 카드 스타일 */
    .history-card {
        background-color: #1e1e2e;
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #2d2d3f;
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


# 4. 상태 변경 함수 정의
def start_test():
    """테스트를 시작하고 무작위 대기 시간을 설정합니다."""
    st.session_state.state = "WAITING"
    st.session_state.reaction_time = None


def handle_click():
    """초록색으로 바뀌었을 때 클릭한 시간을 측정합니다."""
    if st.session_state.state == "CLICK":
        # 현재 시간과 초록색으로 바뀐 시간의 차이를 계산 (초 -> 밀리초 변환)
        end_time = time.perf_counter()
        res = int((end_time - st.session_state.start_time) * 1000)
        st.session_state.reaction_time = res
        st.session_state.history.append(res)  # 기록 저장
        st.session_state.state = "RESULT"


def handle_too_early():
    """너무 일찍 클릭했을 때의 처리"""
    st.session_state.state = "TOO_EARLY"


def reset_all():
    """전체 기록 및 상태 초기화"""
    st.session_state.state = "READY"
    st.session_state.history = []
    st.session_state.reaction_time = None


# 5. 메인 헤더
st.markdown('<div class="title-text">⚡ 반응속도 테스트</div>', unsafe_allow_html=True)
st.markdown('<div class="desc-text">초록색으로 바뀌는 순간 빛의 속도로 클릭하세요!</div>', unsafe_allow_html=True)


# 6. 메인 테스트 영역 (상태에 따른 UI 변경)
# ----------------------------------------------------
# [STATE 1] READY: 시작 전 대기 상태
# ----------------------------------------------------
if st.session_state.state == "READY":
    st.info("준비되셨으면 아래 **'테스트 시작'** 버튼을 누르세요.")
    st.button("🚀 테스트 시작", on_click=start_test, type="primary", use_container_width=True)


# ----------------------------------------------------
# [STATE 2] WAITING: 빨간색 화면 (무작위 대기 중)
# ----------------------------------------------------
elif st.session_state.state == "WAITING":
    # 빨간색 경고 상태 카드
    st.markdown("""
        <div style="
            background-color: #e74c3c;
            border-radius: 15px;
            padding: 3rem 1rem;
            text-align: center;
            color: white;
            font-size: clamp(1.5rem, 5vw, 2.5rem);
            font-weight: bold;
            box-shadow: 0 0 20px rgba(231, 76, 60, 0.4);
            margin-bottom: 1rem;
        ">
            🔴 초록색으로 바뀔 때까지 기다리세요...
        </div>
    """, unsafe_allow_html=True)

    # 실수로 일찍 누르는 것을 감지하는 버튼
    st.button("⚠️ 지금 누르면 안 돼요!", on_click=handle_too_early, use_container_width=True)

    # 1.5초 ~ 4.0초 사이의 random 대기 시간 생성
    wait_time = random.uniform(1.5, 4.0)
    time.sleep(wait_time)

    # 대기 시간이 끝났을 때 사용자가 '성급함' 상태로 전환되지 않았다면 초록색 상태로 변경
    if st.session_state.state == "WAITING":
        st.session_state.start_time = time.perf_counter()  # 고정밀 정밀 시간 기록
        st.session_state.state = "CLICK"
        st.rerun()  # 화면 즉시 새로고침


# ----------------------------------------------------
# [STATE 3] CLICK: 초록색 화면 (클릭 타이밍!)
# ----------------------------------------------------
elif st.session_state.state == "CLICK":
    # 초록색 성공 클릭 안내 화면
    st.markdown("""
        <div style="
            background-color: #2ecc71;
            border-radius: 15px;
            padding: 3rem 1rem;
            text-align: center;
            color: white;
            font-size: clamp(2rem, 6vw, 3rem);
            font-weight: 800;
            box-shadow: 0 0 25px rgba(46, 204, 113, 0.6);
            margin-bottom: 1rem;
        ">
            🟢 지금 클릭하세요!
        </div>
    """, unsafe_allow_html=True)

    # 클릭 반응 버튼
    st.button("💥 클릭!", on_click=handle_click, type="primary", use_container_width=True)


# ----------------------------------------------------
# [STATE 4] TOO_EARLY: 너무 일찍 클릭한 경우
# ----------------------------------------------------
elif st.session_state.state == "TOO_EARLY":
    st.error("⚠️ 너무 일찍 클릭했습니다! 초록색으로 바뀐 후에 눌러주세요.")
    st.button("🔄 다시 시도", on_click=start_test, type="primary", use_container_width=True)


# ----------------------------------------------------
# [STATE 5] RESULT: 측정 결과 출력
# ----------------------------------------------------
elif st.session_state.state == "RESULT":
    ms = st.session_state.reaction_time
    
    # 반응속도 등급 판정
    if ms < 200:
        grade = "⚡ 신의 반응속도!"
    elif ms < 250:
        grade = "🥇 프로게이머 수준!"
    elif ms < 320:
        grade = "🥈 평균 이상의 빠른 속도!"
    else:
        grade = "🥉 조금 더 집중해 보세요!"

    st.markdown(f"""
        <div style="
            background-color: #1e1e2e;
            border-radius: 15px;
            padding: 2rem;
            text-align: center;
            border: 2px solid #00f2fe;
            margin-bottom: 1rem;
        ">
            <h3 style="color: #a0a0b0; margin:0;">측정 결과</h3>
            <h1 style="color: #00f2fe; font-size: 3.5rem; margin: 0.5rem 0;">{ms} ms</h1>
            <p style="font-size: 1.3rem; font-weight: bold; margin:0;">{grade}</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.button("🔄 다시 하기", on_click=start_test, type="primary", use_container_width=True)
    with col2:
        st.button("🏠 처음으로", on_click=lambda: setattr(st.session_state, 'state', 'READY'), use_container_width=True)


# ----------------------------------------------------
# 7. 기록 및 통계 표시 구역
# ----------------------------------------------------
if st.session_state.history:
    st.markdown("---")
    st.write("📊 **내 기록 및 통계**")
    
    history = st.session_state.history
    avg_speed = int(sum(history) / len(history))
    best_speed = min(history)
    
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("시도 횟수", f"{len(history)}회")
    m_col2.metric("최고 기록", f"{best_speed} ms")
    m_col3.metric("평균 속도", f"{avg_speed} ms")

    # 최근 5개 기록 시각화 (기본 line_chart 활용)
    st.caption("📈 시도별 반응속도 변화 (ms)")
    st.line_chart(history)

    if st.button("🗑️ 기록 초기화"):
        reset_all()
        st.rerun()
