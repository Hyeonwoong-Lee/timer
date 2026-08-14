import time
import streamlit as st

# 1. 페이지 기본 설정 (타이틀, 레이아웃, 아이콘)
st.set_page_config(
    page_title="⏱️ 나만의 다크테마 타이머",
    page_icon="⏱️",
    layout="centered"
)

# 2. 세션 상태(Session State) 초기화
if "running" not in st.session_state:
    st.session_state.running = False  # 타이머 실행 여부
if "paused" not in st.session_state:
    st.session_state.paused = False  # 일시정지 여부
if "total_seconds" not in st.session_state:
    st.session_state.total_seconds = 0  # 전체 설정 시간(초)
if "remaining_seconds" not in st.session_state:
    st.session_state.remaining_seconds = 0  # 남은 시간(초)
if "end_time" not in st.session_state:
    st.session_state.end_time = None  # 종료 예정 기준 시간 (time.monotonic 기준)
if "pause_start_time" not in st.session_state:
    st.session_state.pause_start_time = None  # 일시정지 시작 시간
if "completed" not in st.session_state:
    st.session_state.completed = False  # 타이머 완료 여부
if "input_minutes" not in st.session_state:
    st.session_state.input_minutes = 1  # 입력창 기본 분
if "input_seconds" not in st.session_state:
    st.session_state.input_seconds = 0  # 입력창 기본 초


# 3. 다크 테마 커스텀 CSS 스타일 적용
st.markdown("""
    <style>
    /* 전체 배경을 어둡게 설정 */
    .stApp {
        background-color: #121218;
        color: #e0e0e0;
    }
    
    /* 어두운 카드 스타일 (네온 글로우 효과 추가) */
    .timer-card {
        background-color: #1e1e2e;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), 0 0 15px rgba(0, 242, 254, 0.1);
        border: 1px solid #2d2d3f;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* 다크 테마 전용 네온 스타일 타이머 텍스트 */
    .timer-display {
        font-size: clamp(3.5rem, 13vw, 6.5rem);
        font-weight: 800;
        color: #00f2fe;
        text-shadow: 0 0 20px rgba(0, 242, 254, 0.4);
        font-family: 'Courier New', Courier, monospace;
        letter-spacing: 3px;
        margin: 1rem 0;
    }

    /* 입력 폼 라벨 글자 색상 수정 */
    .stNumberInput label {
        color: #b0b0c0 !important;
    }

    /* 버튼 스타일 다크모드 최적화 */
    .stButton > button {
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.2s ease;
        background-color: #2b2b3d;
        color: #ffffff;
        border: 1px solid #3d3d52;
    }
    .stButton > button:hover {
        background-color: #3b3b54;
        border-color: #00f2fe;
        color: #00f2fe;
    }
    </style>
""", unsafe_allow_html=True)


# 4. 빠른 설정 버튼 클릭 시 동작하는 함수
def set_quick_time(minutes):
    """지정된 분 단위로 타이머 시간을 세팅합니다."""
    if not st.session_state.running:
        st.session_state.input_minutes = minutes
        st.session_state.input_seconds = 0


# 5. 메인 앱 UI 헤더 (다크모드용 밝은 제목 글자)
st.markdown("<h1 style='text-align: center; color: #ffffff;'>⏱️ 나만의 다크테마 타이머</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a0a0b0;'>눈이 편안한 다크모드 반응형 카운트다운!</p>", unsafe_allow_html=True)

# 카드 형태의 컨테이너 시작
with st.container():
    st.markdown('<div class="timer-card">', unsafe_allow_html=True)

    # ----------------------------------------------------
    # [입력 및 빠른 설정 구역] - 타이머 동작 중에는 비활성화
    # ----------------------------------------------------
    is_disabled = st.session_state.running or st.session_state.paused

    # 1분, 3분, 5분, 10분 빠른 설정 버튼
    st.markdown("<p style='color: #d0d0e0; font-weight: bold;'>⚡ 빠른 시간 설정</p>", unsafe_allow_html=True)
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    with q_col1:
        if st.button("1분", use_container_width=True, disabled=is_disabled):
            set_quick_time(1)
    with q_col2:
        if st.button("3분", use_container_width=True, disabled=is_disabled):
            set_quick_time(3)
    with q_col3:
        if st.button("5분", use_container_width=True, disabled=is_disabled):
            set_quick_time(5)
    with q_col4:
        if st.button("10분", use_container_width=True, disabled=is_disabled):
            set_quick_time(10)

    # 분/초 수동 입력창
    col_m, col_s = st.columns(2)
    with col_m:
        minutes = st.number_input(
            "분 (Minutes)",
            min_value=0,
            max_value=180,
            key="input_minutes",
            disabled=is_disabled
        )
    with col_s:
        seconds = st.number_input(
            "초 (Seconds)",
            min_value=0,
            max_value=59,
            key="input_seconds",
            disabled=is_disabled
        )

    # ----------------------------------------------------
    # [시간 계산 및 타이머 실행 함수 정의]
    # ----------------------------------------------------
    def start_timer():
        """타이머를 최초 시작합니다."""
        total = minutes * 60 + seconds
        if total <= 0:
            st.error("⚠️ 0초보다 큰 시간을 설정해 주세요!")
            return
        
        st.session_state.total_seconds = total
        st.session_state.remaining_seconds = total
        st.session_state.end_time = time.monotonic() + total
        st.session_state.running = True
        st.session_state.paused = False
        st.session_state.completed = False

    def pause_timer():
        """타이머를 일시정지합니다."""
        if st.session_state.running and not st.session_state.paused:
            st.session_state.paused = True
            st.session_state.running = False
            st.session_state.pause_start_time = time.monotonic()

    def resume_timer():
        """일시정지된 타이머를 다시 진행합니다."""
        if st.session_state.paused:
            paused_duration = time.monotonic() - st.session_state.pause_start_time
            st.session_state.end_time += paused_duration
            st.session_state.paused = False
            st.session_state.running = True

    def reset_timer():
        """타이머를 초기화합니다."""
        st.session_state.running = False
        st.session_state.paused = False
        st.session_state.completed = False
        st.session_state.total_seconds = 0
        st.session_state.remaining_seconds = 0
        st.session_state.end_time = None

    # ----------------------------------------------------
    # [제어 버튼 구역]
    # ----------------------------------------------------
    st.write("")
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 1, 1, 1])

    with btn_col1:
        if not st.session_state.running and not st.session_state.paused:
            st.button("▶️ 시작", on_click=start_timer, type="primary", use_container_width=True)
        elif st.session_state.running:
            st.button("⏸️ 일시정지", on_click=pause_timer, use_container_width=True)
        elif st.session_state.paused:
            st.button("▶️ 계속", on_click=resume_timer, type="primary", use_container_width=True)

    with btn_col2:
        st.button("🔄 초기화", on_click=reset_timer, use_container_width=True)

    # ----------------------------------------------------
    # [실시간 타이머 디스플레이 구역 (st.fragment 사용)]
    # ----------------------------------------------------
    @st.fragment(run_every=0.1 if st.session_state.running else None)
    def render_timer():
        if st.session_state.running and st.session_state.end_time:
            now = time.monotonic()
            rem = max(0, int(st.session_state.end_time - now))
            st.session_state.remaining_seconds = rem

            if rem <= 0:
                st.session_state.running = False
                st.session_state.completed = True

        rem_sec = st.session_state.remaining_seconds
        display_m = rem_sec // 60
        display_s = rem_sec % 60
        time_str = f"{display_m:02d}:{display_s:02d}"

        # 큰 네온 타이머 시계 표시
        st.markdown(f'<div class="timer-display">{time_str}</div>', unsafe_allow_html=True)

        # 진행률 막대(Progress Bar) 표시
        if st.session_state.total_seconds > 0:
            progress = rem_sec / st.session_state.total_seconds
            progress = max(0.0, min(1.0, progress))
            st.progress(progress)
        else:
            st.progress(1.0)

        # 타이머 완료 시 효과 및 축하 메시지
        if st.session_state.completed:
            st.balloons()
            st.success("🎉 설정한 시간이 완료되었습니다!")

    # 실시간 프래그먼트 호출
    render_timer()

    st.markdown('</div>', unsafe_allow_html=True)
