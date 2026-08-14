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


# 3. 화면 전체 클릭 가능 커스텀 CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #121218;
        color: #ffffff;
    }
    
    /* 타이틀 및 설명 */
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
       [화면 전체 클릭 감지 핵심 기술]
       Streamlit의 st.button 영역을 카드 크기 전체로 확장하고 
       투명하게 만들어 화면 어디를 눌러도 클릭되게 만듭니다.
    */
    .full-screen-target {
        position: relative;
        width: 100%;
        min-height: 320px;
        border-radius: 20px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 2rem;
        user-select: none;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    /* Streamlit 기본 버튼을 카드 전체로 키우고 투명화 */
    .full-click-overlay div[data-testid="stButton"] {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 10;
    }
    .full-click-overlay div[data-testid="stButton"] > button {
        width: 100% !important;
        height: 100% !important;
        opacity: 0 !important; /* 버튼을 투명하게 만들어 배경 카드가 보이게 함 */
        cursor: pointer !important;
    }

    /* 상태별 배경 스타일 */
    .bg-ready {
        background-color: #1e1e2e;
        border: 2px dashed #3d3d52;
    }
    .bg-waiting {
        background-color: #ce392b;
        box-shadow: 0 0 30px rgba(206, 57, 43, 0.4);
    }
    .bg-click {
        background-color: #27ae60;
        box-shadow: 0 0 40px rgba(39, 174, 96, 0.6);
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

def handle_screen_click():
    """화면 어디든 클릭했을 때 실행되는 통합 함수"""
    current_state = st.session_state.state
    
    if current_state == "READY":
        start_test()
    elif current_state == "WAITING":
        # 빨간색일 때 눌렀으므로 성급함 처리
        st.session_state.state = "TOO_EARLY"
    elif current_state == "CLICK":
        # 초록색일 때 누른 반응속도 정밀 측정
        end_time = time.perf_counter()
        ms = int((end_time - st.session_state.start_time) * 1000)
        st.session_state.reaction_time = ms
        st.session_state.history.append(ms)
        st.session_state.state = "RESULT"

def reset_all():
    """기록 및 상태 전체 초기화"""
    st.session_state.state = "READY"
    st.session_state.history = []
    st.session_state.reaction_time = None


# 5. 헤더 구역
st.markdown('<div class="title-text">⚡ 반응속도 테스트</div>', unsafe_allow_html=True)
st.markdown('<div class="desc-text">상자 안 화면 어디를 터치/클릭해도 작동합니다!</div>', unsafe_allow_html=True)


# 6. 메인 테스트 구역 (전체 클릭 타겟 적용)
# ----------------------------------------------------
# [STATE 1] READY: 시작 전
# ----------------------------------------------------
if st.session_state.state == "READY":
    st.markdown('<div class="full-click-overlay" style="position: relative;">', unsafe_allow_html=True)
    
    # 시각적 카드 화면
    st.markdown("""
        <div class="full-screen-target bg-ready">
            <h2 style="margin: 0; color: #ffffff;">🚀 클릭하여 시작하기</h2>
            <p style="color: #a0a0b0; margin-top: 0.5rem;">화면 어디든 누르면 테스트가 시작됩니다.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 카드 전체를 덮는 투명 버튼 (클릭 감지용)
    st.button("시작", key="btn_ready", on_click=handle_screen_click)
    st.markdown('</div>', unsafe_allow_html=True)


# ----------------------------------------------------
# [STATE 2] WAITING: 빨간색 (대기 중)
# ----------------------------------------------------
elif st.session_state.state == "WAITING":
    st.markdown('<div class="full-click-overlay" style="position: relative;">', unsafe_allow_html=True)
    
    # 빨간색 화면
    st.markdown("""
        <div class="full-screen-target bg-waiting">
            <h1 style="font-size: clamp(2rem, 6vw, 3.5rem); margin: 0; color: #ffffff;">🔴 대기하세요...</h1>
            <p style="color: #fce4e4; margin-top: 0.5rem;">초록색으로 바뀌기 전 누르면 감점됩니다!</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 실수로 일찍 누르는 것을 감지하는 투명 버튼
    st.button("대기중클릭", key="btn_waiting", on_click=handle_screen_click)
    st.markdown('</div>', unsafe_allow_html=True)

    # 1.5 ~ 4.0초 랜덤 대기
    wait_time = random.uniform(1.5, 4.0)
    time.sleep(wait_time)

    # 대기 후 누르지 않았다면 초록색(CLICK) 상태로 변경
    if st.session_state.state == "WAITING":
        st.session_state.start_time = time.perf_counter()
        st.session_state.state = "CLICK"
        st.rerun()


# ----------------------------------------------------
# [STATE 3] CLICK: 초록색 (지금 누르세요!)
# ----------------------------------------------------
elif st.session_state.state == "CLICK":
    st.markdown('<div class="full-click-overlay" style="position: relative;">', unsafe_allow_html=True)
    
    # 초록색 화면
    st.markdown("""
        <div class="full-screen-target bg-click">
            <h1 style="font-size: clamp(2.5rem, 8vw, 4rem); margin: 0; color: #ffffff; font-weight: 900;">🟢 지금 클릭!</h1>
            <p style="color: #e8f8f0; margin-top: 0.5rem;">화면 어디든 최대한 빠르게 누르세요!</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 반응속도 클릭을 감지하는 투명 버튼
    st.button("지금클릭", key="btn_click", on_click=handle_screen_click)
    st.markdown('</div>', unsafe_allow_html=True)


# ----------------------------------------------------
# [STATE 4] TOO_EARLY: 성급함 (너무 일찍 누름)
# ----------------------------------------------------
elif st.session_state.state == "TOO_EARLY":
    st.markdown('<div class="full-click-overlay" style="position: relative;">', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="full-screen-target bg-early">
            <h2 style="margin: 0; color: #ffffff;">⚠️ 너무 일찍 눌렀습니다!</h2>
            <p style="color: #fdebd0; margin-top: 0.5rem;">초록색으로 바뀐 후에 눌러주세요.<br><b>[화면을 누르면 다시 시도합니다]</b></p>
        </div>
    """, unsafe_allow_html=True)
    
    st.button("다시시도", key="btn_early", on_click=start_test)
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
            padding: 2rem;
            text-align: center;
            border: 2px solid #00f2fe;
            margin-bottom: 1rem;
        ">
            <p style="color: #a0a0b0; margin: 0;">측정된 반응속도</p>
            <h1 style="color: #00f2fe; font-size: 3.5rem; margin: 0.5rem 0;">{ms} ms</h1>
            <p style="font-size: 1.2rem; font-weight: bold; margin: 0;">{grade}</p>
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
