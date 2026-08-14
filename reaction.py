import time
import random
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="⚡ 반응속도 테스트",
    page_icon="⚡",
    layout="centered"
)

# 2. 세션 상태 초기화
if "state" not in st.session_state:
    st.session_state.state = "READY"
if "start_time" not in st.session_state:
    st.session_state.start_time = 0
if "reaction_time" not in st.session_state:
    st.session_state.reaction_time = None
if "history" not in st.session_state:
    st.session_state.history = []


# 3. 브라우저 창 전체(100% 화면)를 덮는 강제 CSS 오버레이
st.markdown("""
    <style>
    /* 웹페이지 기본 여백 완전히 제거 */
    .stAppViewContainer, .main, .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }

    /* 
       [핵심!] 브라우저 창 전체(100vw, 100vh)를 완전히 덮는 고정 레이어
       position: fixed로 설정하여 화면 스크롤이나 여백 상관없이 창 전체를 클릭 타겟으로 만듭니다.
    */
    .full-window-overlay {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 99999 !important;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        user-select: none;
        cursor: pointer;
    }

    /* 화면 전체를 덮는 투명 버튼 스타일 */
    div[data-testid="stButton"].click-all-target {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 100000 !important;
    }
    
    div[data-testid="stButton"].click-all-target > button {
        width: 100vw !important;
        height: 100vh !important;
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        opacity: 0 !important;
        cursor: pointer !important;
    }

    /* 상태별 배경 스타일 */
    .bg-ready {
        background-color: #121218;
    }
    .bg-waiting {
        background-color: #ce392b;
    }
    .bg-click {
        background-color: #27ae60;
    }
    .bg-early {
        background-color: #d35400;
    }
    </style>
""", unsafe_allow_html=True)


# 4. 이벤트 처리 함수
def start_test():
    """테스트 시작 및 무작위 대기 세팅"""
    st.session_state.state = "WAITING"
    st.session_state.reaction_time = None

def handle_click():
    """화면 창 내 아무 곳이나 클릭했을 때 호출되는 통합 함수"""
    current_state = st.session_state.state
    
    if current_state == "READY":
        start_test()
    elif current_state == "WAITING":
        # 빨간색일 때 클릭 → 성급함 처리
        st.session_state.state = "TOO_EARLY"
    elif current_state == "CLICK":
        # 초록색일 때 클릭 → 고정밀 정밀 시간 측정
        end_time = time.perf_counter()
        ms = int((end_time - st.session_state.start_time) * 1000)
        st.session_state.reaction_time = ms
        st.session_state.history.append(ms)
        st.session_state.state = "RESULT"

def reset_all():
    """기록 및 상태 초기화"""
    st.session_state.state = "READY"
    st.session_state.history = []
    st.session_state.reaction_time = None


# 5. 테스트 화면 (결과 화면을 제외하고는 창 전체가 클릭 패널로 변환)
# ----------------------------------------------------
# [STATE 1] READY: 시작 전 (창 전체 터치 가능)
# ----------------------------------------------------
if st.session_state.state == "READY":
    st.markdown("""
        <div class="full-window-overlay bg-ready">
            <h1 style="font-size: clamp(2.5rem, 8vw, 4.5rem); margin: 0; color: #ffffff;">⚡ 반응속도 테스트</h1>
            <p style="color: #00f2fe; font-size: clamp(1.2rem, 4vw, 2rem); margin-top: 1.5rem; font-weight: bold;">
                🖥️ 화면 아무 곳이나 누르면 시작됩니다!
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # 창 전체 크기의 투명 버튼
    st.button("시작", key="btn_ready", on_click=handle_click)
    
    # CSS 클래스를 버튼에 강제 주입하여 창 전체로 확충
    st.markdown("""
        <script>
            var btns = window.parent.document.querySelectorAll('div[data-testid="stButton"]');
            btns[btns.length - 1].classList.add('click-all-target');
        </script>
    """, unsafe_allow_html=True)


# ----------------------------------------------------
# [STATE 2] WAITING: 빨간색 (대기 중 - 창 전체 터치 감지)
# ----------------------------------------------------
elif st.session_state.state == "WAITING":
    st.markdown("""
        <div class="full-window-overlay bg-waiting">
            <h1 style="font-size: clamp(3rem, 10vw, 6rem); margin: 0; color: #ffffff; font-weight: 900;">🔴 대기하세요...</h1>
            <p style="color: #fce4e4; font-size: clamp(1.2rem, 3.5vw, 1.8rem); margin-top: 1.5rem;">
                초록색으로 바뀌기 전 화면을 누르면 실패합니다!
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.button("대기", key="btn_waiting", on_click=handle_click)
    
    st.markdown("""
        <script>
            var btns = window.parent.document.querySelectorAll('div[data-testid="stButton"]');
            btns[btns.length - 1].classList.add('click-all-target');
        </script>
    """, unsafe_allow_html=True)

    # 무작위 대기 시간 (1.5초 ~ 4.0초)
    wait_time = random.uniform(1.5, 4.0)
    time.sleep(wait_time)

    # 누르지 않고 대기했으면 초록색(CLICK) 화면으로 변환
    if st.session_state.state == "WAITING":
        st.session_state.start_time = time.perf_counter()
        st.session_state.state = "CLICK"
        st.rerun()


# ----------------------------------------------------
# [STATE 3] CLICK: 초록색 (지금 누르세요! - 창 전체 터치 감지)
# ----------------------------------------------------
elif st.session_state.state == "CLICK":
    st.markdown("""
        <div class="full-window-overlay bg-click">
            <h1 style="font-size: clamp(3.5rem, 12vw, 7rem); margin: 0; color: #ffffff; font-weight: 900;">🟢 지금 클릭!!!</h1>
            <p style="color: #e8f8f0; font-size: clamp(1.3rem, 4vw, 2rem); margin-top: 1.5rem; font-weight: bold;">
                화면 아무 데나 빠르게 누르세요!
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.button("클릭", key="btn_click", on_click=handle_click)
    
    st.markdown("""
        <script>
            var btns = window.parent.document.querySelectorAll('div[data-testid="stButton"]');
            btns[btns.length - 1].classList.add('click-all-target');
        </script>
    """, unsafe_allow_html=True)


# ----------------------------------------------------
# [STATE 4] TOO_EARLY: 성급함 (창 전체 터치 감지)
# ----------------------------------------------------
elif st.session_state.state == "TOO_EARLY":
    st.markdown("""
        <div class="full-window-overlay bg-early">
            <h1 style="font-size: clamp(2.5rem, 8vw, 4.5rem); margin: 0; color: #ffffff;">⚠️ 너무 일찍 눌렀습니다!</h1>
            <p style="color: #fdebd0; font-size: clamp(1.2rem, 3.5vw, 1.8rem); margin-top: 1.5rem;">
                초록색으로 변한 후에 눌러야 합니다.<br><br><b>[화면 아무 곳이나 누르면 다시 시작]</b>
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.button("다시시도", key="btn_early", on_click=start_test)
    
    st.markdown("""
        <script>
            var btns = window.parent.document.querySelectorAll('div[data-testid="stButton"]');
            btns[btns.length - 1].classList.add('click-all-target');
        </script>
    """, unsafe_allow_html=True)


# ----------------------------------------------------
# [STATE 5] RESULT: 결과 화면 (기록 및 다시 시작)
# ----------------------------------------------------
elif st.session_state.state == "RESULT":
    ms = st.session_state.reaction_time
    
    if ms < 200:
        grade = "⚡ 신의 반응속도!"
    elif ms < 250:
        grade = "🥇 프로게이머 수준!"
    elif ms < 320:
        grade = "🥈 평균 이상의 빠른 속도!"
    else:
        grade = "🥉 조금 더 연습해 보세요!"

    st.markdown(f"""
        <div style="
            background-color: #1e1e2e;
            border-radius: 20px;
            padding: 2.5rem 1.5rem;
            text-align: center;
            border: 2px solid #00f2fe;
            margin: 2rem 1rem 1rem 1rem;
        ">
            <p style="color: #a0a0b0; margin: 0; font-size: 1.1rem;">측정된 반응속도</p>
            <h1 style="color: #00f2fe; font-size: clamp(3rem, 8vw, 4.5rem); margin: 0.5rem 0;">{ms} ms</h1>
            <p style="font-size: 1.3rem; font-weight: bold; margin: 0; color: #ffffff;">{grade}</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.button("🔄 다시 하기", on_click=start_test, type="primary", use_container_width=True)
    with col2:
        st.button("🏠 처음으로", on_click=lambda: setattr(st.session_state, 'state', 'READY'), use_container_width=True)

    # 내 기록 및 통계 구역
    if st.session_state.history:
        st.markdown("<hr style='border-color: #2d2d3f;'>", unsafe_allow_html=True)
        st.write("📊 **내 기록 및 통계**")
        
        history = st.session_state.history
        avg_speed = int(sum(history) / len(history))
        best_speed = min(history)
        
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("시도 횟수", f"{len(history)}회")
        m_col2.metric("최고 기록", f"{best_speed} ms")
        m_col3.metric("평균 속도", f"{avg_speed} ms")

        st.caption("📈 시도별 반응속도 변화 (ms)")
        st.line_chart(history)

        if st.button("🗑️ 기록 초기화"):
            reset_all()
            st.rerun()
