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


# 3. 창 전체(Full Window) 클릭 감지 CSS
st.markdown("""
    <style>
    /* 전체 브라우저 배경 */
    .stApp {
        background-color: #121218;
        color: #ffffff;
    }
    
    /* 헤더 및 설명 */
    .title-text {
        text-align: center;
        font-size: clamp(1.8rem, 5vw, 2.8rem);
        font-weight: 800;
        margin-bottom: 0.3rem;
    }
    .desc-text {
        text-align: center;
        color: #a0a0b0;
        font-size: clamp(0.9rem, 2.5vw, 1.1rem);
        margin-bottom: 1rem;
    }

    /* 
       [핵심!] 창 전체 클릭 감지 오버레이
       position: fixed로 뷰포트(화면 전체)를 덮어 어떤 위치를 눌러도 감지합니다.
    */
    .full-window-card {
        position: relative;
        width: 100%;
        height: 60vh; /* 화면 높이의 60%를 채우는 거대 영역 */
        min-height: 350px;
        border-radius: 20px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 2rem;
        user-select: none;
    }

    /* Streamlit 버튼을 화면 전체 영역으로 확장하고 완전 투명화 */
    div[data-testid="stButton"].full-screen-btn {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        z-index: 9999 !important;
    }
    
    div[data-testid="stButton"].full-screen-btn > button {
        width: 100% !important;
        height: 100% !important;
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        opacity: 0 !important;
        cursor: pointer !important;
    }

    /* 상태별 배경 스타일 */
    .bg-ready {
        background-color: #1e1e2e;
        border: 2px dashed #3d3d52;
    }
    .bg-waiting {
        background-color: #ce392b;
        box-shadow: 0 0 35px rgba(206, 57, 43, 0.5);
    }
    .bg-click {
        background-color: #27ae60;
        box-shadow: 0 0 45px rgba(39, 174, 96, 0.7);
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
    """창 내 아무 곳이나 클릭했을 때 호출되는 함수"""
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


# 5. 헤더 구역
st.markdown('<div class="title-text">⚡ 반응속도 테스트</div>', unsafe_allow_html=True)
st.markdown('<div class="desc-text">🖥️ 모니터/스마트폰 화면 창 어디를 터치해도 즉시 인식됩니다!</div>', unsafe_allow_html=True)


# 6. 메인 테스트 구역 (창 전체 클릭 타겟)
# ----------------------------------------------------
# [STATE 1] READY: 시작 전
# ----------------------------------------------------
if st.session_state.state == "READY":
    st.markdown('<div style="position: relative;">', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="full-window-card bg-ready">
            <h1 style="font-size: clamp(2rem, 6vw, 3.5rem); margin: 0; color: #ffffff;">🚀 아무 곳이나 클릭!</h1>
            <p style="color: #a0a0b0; font-size: 1.2rem; margin-top: 1rem;">창 안의 모든 영역이 반응합니다.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 영역 전체를 덮는 투명 버튼
    st.button("시작", key="btn_ready", on_click=handle_click, help="", type="secondary")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # CSS 클래스 주입
    st.markdown("""
        <script>
            var btns = window.parent.document.querySelectorAll('div[data-testid="stButton"]');
            btns[btns.length - 1].classList.add('full-screen-btn');
        </script>
    """, unsafe_allow_html=True)


# ----------------------------------------------------
# [STATE 2] WAITING: 빨간색 (대기 중)
# ----------------------------------------------------
elif st.session_state.state == "WAITING":
    st.markdown('<div style="position: relative;">', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="full-window-card bg-waiting">
            <h1 style="font-size: clamp(2.5rem, 8vw, 4.5rem); margin: 0; color: #ffffff; font-weight: 900;">🔴 대기하세요...</h1>
            <p style="color: #fce4e4; font-size: 1.2rem; margin-top: 1rem;">초록색으로 바뀌기 전 클릭하면 실패합니다!</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.button("대기", key="btn_waiting", on_click=handle_click, type="secondary")
    st.markdown('</div>', unsafe_allow_html=True)

    # 무작위 대기 시간 (1.5초 ~ 4.0초)
    wait_time = random.uniform(1.5, 4.0)
    time.sleep(wait_time)

    # 누르지 않고 무사히 대기했으면 초록색(CLICK) 화면으로 변환
    if st.session_state.state == "WAITING":
        st.session_state.start_time = time.perf_counter()
        st.session_state.state = "CLICK"
        st.rerun()


# ----------------------------------------------------
# [STATE 3] CLICK: 초록색 (지금 누르세요!)
# ----------------------------------------------------
elif st.session_state.state == "CLICK":
    st.markdown('<div style="position: relative;">', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="full-window-card bg-click">
            <h1 style="font-size: clamp(3rem, 10vw, 5.5rem); margin: 0; color: #ffffff; font-weight: 900;">🟢 지금 클릭!!!</h1>
            <p style="color: #e8f8f0; font-size: 1.3rem; margin-top: 1rem;">빛의 속도로 화면을 누르세요!</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.button("클릭", key="btn_click", on_click=handle_click, type="secondary")
    st.markdown('</div>', unsafe_allow_html=True)


# ----------------------------------------------------
# [STATE 4] TOO_EARLY: 성급함
# ----------------------------------------------------
elif st.session_state.state == "TOO_EARLY":
    st.markdown('<div style="position: relative;">', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="full-window-card bg-early">
            <h1 style="font-size: clamp(2rem, 6vw, 3.5rem); margin: 0; color: #ffffff;">⚠️ 너무 일찍 눌렀습니다!</h1>
            <p style="color: #fdebd0; font-size: 1.2rem; margin-top: 1rem;">초록색으로 변한 후에 눌러야 합니다.<br><b>[아무 곳이나 누르면 다시 시작합니다]</b></p>
        </div>
    """, unsafe_allow_html=True)
    
    st.button("다시시도", key="btn_early", on_click=start_test, type="secondary")
    st.markdown('</div>', unsafe_allow_html=True)


# ----------------------------------------------------
# [STATE 5] RESULT: 결과 화면
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
            margin-bottom: 1rem;
        ">
            <p style="color: #a0a0b0; margin: 0; font-size: 1.1rem;">측정된 반응속도</p>
            <h1 style="color: #00f2fe; font-size: clamp(3rem, 8vw, 4.5rem); margin: 0.5rem 0;">{ms} ms</h1>
            <p style="font-size: 1.3rem; font-weight: bold; margin: 0;">{grade}</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.button("🔄 다시 하기", on_click=start_test, type="primary", use_container_width=True)
    with col2:
        st.button("🏠 처음으로", on_click=lambda: setattr(st.session_state, 'state', 'READY'), use_container_width=True)


# 7. 내 기록 및 통계 구역
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

    st.caption("📈 시도별 반응속도 변화 (ms)")
    st.line_chart(history)

    if st.button("🗑️ 기록 초기화"):
        reset_all()
        st.rerun()
