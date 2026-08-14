import streamlit as st
import time

# --- 1. 페이지 기본 설정 ---
st.set_page_config(page_title="나만의 반응형 타이머", page_icon="⏱️", layout="centered")

# --- 2. CSS 스타일 적용 (다크 테마용 반응형 디자인) ---
st.markdown("""
    <style>
    /* 다크 테마에 어울리는 진한 회색 카드 디자인 */
    .timer-card {
        background-color: #2b2b2b; /* 진한 회색 배경 */
        border: 1px solid #444444; /* 테두리를 살짝 주어 입체감 부여 */
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.5); /* 그림자를 더 크고 진하게 설정 */
        margin: 20px 0;
    }
    
    /* 글자 색상을 밝게 하고 크기를 자동으로 조절 */
    .timer-text {
        color: #ffffff; /* 글자를 순백색으로 설정 */
        text-shadow: 0px 2px 10px rgba(255, 255, 255, 0.2); /* 글자에 살짝 빛나는 효과 */
        font-size: clamp(4rem, 15vw, 8rem);
        font-weight: 900;
        margin-bottom: 20px;
        font-variant-numeric: tabular-nums; 
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 상태 저장소(Session State) 초기화 ---
if 'status' not in st.session_state:
    st.session_state.status = 'stopped'  
if 'total_seconds' not in st.session_state:
    st.session_state.total_seconds = 0   
if 'remaining_seconds' not in st.session_state:
    st.session_state.remaining_seconds = 0 
if 'end_time' not in st.session_state:
    st.session_state.end_time = 0.0      
if 'balloons_shown' not in st.session_state:
    st.session_state.balloons_shown = False 
if 'input_min' not in st.session_state:
    st.session_state.input_min = 0       
if 'input_sec' not in st.session_state:
    st.session_state.input_sec = 0       

# --- 4. 타이머 제어 함수들 ---
def start_timer():
    total_sec = (st.session_state.input_min * 60) + st.session_state.input_sec
    if total_sec <= 0:
        st.warning("0초 이상으로 시간을 설정해 주세요!")
        return
    st.session_state.total_seconds = total_sec
    st.session_state.remaining_seconds = total_sec
    st.session_state.end_time = time.monotonic() + total_sec
    st.session_state.status = 'running'
    st.session_state.balloons_shown = False 

def pause_timer():
    st.session_state.status = 'paused'
    st.session_state.remaining_seconds = max(0, st.session_state.end_time - time.monotonic())

def resume_timer():
    st.session_state.status = 'running'
    st.session_state.end_time = time.monotonic() + st.session_state.remaining_seconds

def reset_timer():
    st.session_state.status = 'stopped'
    st.session_state.remaining_seconds = 0
    st.session_state.total_seconds = 0

def set_quick_time(minutes):
    st.session_state.input_min = minutes
    st.session_state.input_sec = 0

# --- 5. UI 화면 구성 ---
st.title("⏱️ 나만의 반응형 타이머 (다크 테마)")

is_disabled = st.session_state.status in ['running', 'paused']

# (1) 시간 설정 영역
col1, col2 = st.columns(2)
with col1:
    st.number_input("분 (Minutes)", min_value=0, max_value=999, step=1, 
                    key="input_min", disabled=is_disabled)
with col2:
    st.number_input("초 (Seconds)", min_value=0, max_value=59, step=1, 
                    key="input_sec", disabled=is_disabled)

# (2) 빠른 설정 버튼 영역 
st.caption("⚡ 빠른 설정")
q_col1, q_col2, q_col3, q_col4 = st.columns(4)
with q_col1:
    if st.button("1분", use_container_width=True, disabled=is_disabled): set_quick_time(1)
with q_col2:
    if st.button("3분", use_container_width=True, disabled=is_disabled): set_quick_time(3)
with q_col3:
    if st.button("5분", use_container_width=True, disabled=is_disabled): set_quick_time(5)
with q_col4:
    if st.button("10분", use_container_width=True, disabled=is_disabled): set_quick_time(10)

st.divider() 

# (3) 제어 버튼 영역
c_col1, c_col2, c_col3 = st.columns(3)

with c_col1:
    if st.session_state.status in ['stopped', 'completed']:
        if st.button("▶️ 시작", use_container_width=True, type="primary"):
            start_timer()
    elif st.session_state.status == 'running':
        if st.button("⏸️ 일시정지", use_container_width=True):
            pause_timer()
    elif st.session_state.status == 'paused':
        if st.button("▶️ 계속", use_container_width=True, type="primary"):
            resume_timer()

with c_col3:
    if st.session_state.status in ['running', 'paused', 'completed']:
        if st.button("🔄 초기화", use_container_width=True):
            reset_timer()

# --- 6. 화면 자동 새로고침(Fragment) 영역 ---
@st.fragment(run_every=1)
def display_timer():
    if st.session_state.status == 'running':
        now = time.monotonic()
        left = st.session_state.end_time - now
        
        if left <= 0:
            st.session_state.status = 'completed'
            st.session_state.remaining_seconds = 0
            if not st.session_state.balloons_shown:
                st.balloons() 
                st.session_state.balloons_shown = True
        else:
            st.session_state.remaining_seconds = left

    left_sec = st.session_state.remaining_seconds
    mins = int(left_sec // 60)
    secs = int(left_sec % 60)

    st.markdown(f"""
        <div class="timer-card">
            <div class="timer-text">{mins:02d}:{secs:02d}</div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.total_seconds > 0:
        progress_val = left_sec / st.session_state.total_seconds
        progress_val = max(0.0, min(1.0, progress_val)) 
    else:
        progress_val = 0.0
    
    st.progress(progress_val)

    if st.session_state.status == 'completed':
        st.success("🎉 시간이 다 되었습니다! 수고하셨어요.")

display_timer()
