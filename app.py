import streamlit as st
import time

# --- 1. 페이지 기본 설정 ---
# 웹 브라우저의 탭 제목과 아이콘, 레이아웃을 설정합니다.
st.set_page_config(page_title="나만의 반응형 타이머", page_icon="⏱️", layout="centered")

# --- 2. CSS 스타일 적용 (반응형 디자인 및 카드 UI) ---
# 스마트폰, 태블릿, PC 어디서든 예쁘게 보이도록 CSS를 추가합니다.
st.markdown("""
    <style>
    /* 카드를 감싸는 배경 스타일 (다크/라이트 모드 모두 어울리게 반투명 사용) */
    .timer-card {
        background-color: rgba(128, 128, 128, 0.1);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
        margin: 20px 0;
    }
    
    /* 화면 크기에 맞춰 글씨가 자동으로 커지고 작아지는 clamp() 기술 */
    /* 최소 4rem, 기본 화면의 15vw, 최대 8rem 크기를 가집니다. */
    .timer-text {
        font-size: clamp(4rem, 15vw, 8rem);
        font-weight: 900;
        margin-bottom: 20px;
        font-variant-numeric: tabular-nums; /* 숫자 폭을 일정하게 맞춰 덜덜거림 방지 */
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 상태 저장소(Session State) 초기화 ---
# 타이머가 새로고침되어도 데이터를 기억하도록 설정합니다.
if 'status' not in st.session_state:
    st.session_state.status = 'stopped'  # 상태: stopped, running, paused, completed
if 'total_seconds' not in st.session_state:
    st.session_state.total_seconds = 0   # 전체 설정 시간 (초)
if 'remaining_seconds' not in st.session_state:
    st.session_state.remaining_seconds = 0 # 남은 시간 (초)
if 'end_time' not in st.session_state:
    st.session_state.end_time = 0.0      # 타이머가 끝나는 실제 시각
if 'balloons_shown' not in st.session_state:
    st.session_state.balloons_shown = False # 풍선 효과가 한 번만 나오도록 방지하는 스위치
if 'input_min' not in st.session_state:
    st.session_state.input_min = 0       # 설정된 '분'
if 'input_sec' not in st.session_state:
    st.session_state.input_sec = 0       # 설정된 '초'

# --- 4. 타이머 제어 함수들 ---

def start_timer():
    """타이머 시작 함수"""
    # 입력된 분과 초를 모두 '초' 단위로 바꿉니다.
    total_sec = (st.session_state.input_min * 60) + st.session_state.input_sec
    
    if total_sec <= 0:
        st.warning("0초 이상으로 시간을 설정해 주세요!")
        return
    
    st.session_state.total_seconds = total_sec
    st.session_state.remaining_seconds = total_sec
    # 단순히 숫자를 빼지 않고, 컴퓨터의 실제 시간(monotonic)을 이용해 끝날 시간을 계산합니다.
    st.session_state.end_time = time.monotonic() + total_sec
    st.session_state.status = 'running'
    st.session_state.balloons_shown = False # 풍선 상태 초기화

def pause_timer():
    """일시정지 함수"""
    st.session_state.status = 'paused'
    # 정지한 시점에 남은 시간을 계산해서 저장합니다.
    st.session_state.remaining_seconds = max(0, st.session_state.end_time - time.monotonic())

def resume_timer():
    """계속하기 함수"""
    st.session_state.status = 'running'
    # 남은 시간을 바탕으로 새로운 종료 시간을 다시 계산합니다.
    st.session_state.end_time = time.monotonic() + st.session_state.remaining_seconds

def reset_timer():
    """초기화 함수"""
    st.session_state.status = 'stopped'
    st.session_state.remaining_seconds = 0
    st.session_state.total_seconds = 0

def set_quick_time(minutes):
    """빠른 설정 버튼용 함수"""
    st.session_state.input_min = minutes
    st.session_state.input_sec = 0

# --- 5. UI 화면 구성 ---
st.title("⏱️ 나만의 반응형 타이머")

# 타이머가 실행 중이거나 일시정지 중일 때는 입력을 막습니다.
is_disabled = st.session_state.status in ['running', 'paused']

# (1) 시간 설정 영역
col1, col2 = st.columns(2)
with col1:
    st.number_input("분 (Minutes)", min_value=0, max_value=999, step=1, 
                    key="input_min", disabled=is_disabled)
with col2:
    st.number_input("초 (Seconds)", min_value=0, max_value=59, step=1, 
                    key="input_sec", disabled=is_disabled)

# (2) 빠른 설정 버튼 영역 (모바일에서는 자동으로 예쁘게 정렬됩니다)
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

st.divider() # 화면 구분선

# (3) 제어 버튼 영역
c_col1, c_col2, c_col3 = st.columns(3)

# 상태에 따라 필요한 버튼만 보여줍니다.
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
    # 실행 중이거나 일시정지 상태일 때만 초기화 버튼 표시
    if st.session_state.status in ['running', 'paused', 'completed']:
        if st.button("🔄 초기화", use_container_width=True):
            reset_timer()

# --- 6. 화면 자동 새로고침(Fragment) 영역 ---
# 1초마다 이 구역만 새로고침되어 전체 화면이 깜빡이지 않습니다.
@st.fragment(run_every=1)
def display_timer():
    # 실행 중일 때 남은 시간 계산
    if st.session_state.status == 'running':
        now = time.monotonic()
        left = st.session_state.end_time - now
        
        # 시간이 다 되었을 때
        if left <= 0:
            st.session_state.status = 'completed'
            st.session_state.remaining_seconds = 0
            if not st.session_state.balloons_shown:
                st.balloons() # 풍선 축하 효과
                st.session_state.balloons_shown = True
        else:
            st.session_state.remaining_seconds = left

    # 남은 시간을 분과 초로 나눕니다.
    left_sec = st.session_state.remaining_seconds
    mins = int(left_sec // 60)
    secs = int(left_sec % 60)

    # 카드 모양 안에 00:00 형태로 크게 출력합니다.
    st.markdown(f"""
        <div class="timer-card">
            <div class="timer-text">{mins:02d}:{secs:02d}</div>
        </div>
    """, unsafe_allow_html=True)

    # 진행률 막대(Progress bar) 계산
    if st.session_state.total_seconds > 0:
        # 0.0 ~ 1.0 사이의 비율로 변환합니다.
        progress_val = left_sec / st.session_state.total_seconds
        progress_val = max(0.0, min(1.0, progress_val)) # 안전장치
    else:
        progress_val = 0.0
    
    st.progress(progress_val)

    # 종료 메시지
    if st.session_state.status == 'completed':
        st.success("🎉 시간이 다 되었습니다! 수고하셨어요.")

# 위에서 정의한 부분(Fragment)을 실제로 화면에 표시합니다.
display_timer()
