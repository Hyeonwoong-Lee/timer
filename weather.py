import random
import datetime
import streamlit as st

# 1. 페이지 기본 설정 (타이틀, 레이아웃, 아이콘)
st.set_page_config(
    page_title="🌤️ 날씨별 옷차림 추천 앱",
    page_icon="🌤️",
    layout="centered"
)

# 2. 세션 상태(Session State) 초기화
if "selected_city" not in st.session_state:
    st.session_state.selected_city = "서울"
if "custom_temp" not in st.session_state:
    st.session_state.custom_temp = 20
if "weather_condition" not in st.session_state:
    st.session_state.weather_condition = "맑음"


# 3. 다크 테마 커스텀 CSS 스타일 적용
st.markdown("""
    <style>
    /* 전체 배경을 깔끔한 다크 모드로 설정 */
    .stApp {
        background-color: #121218;
        color: #ffffff;
    }
    
    /* 중앙 메인 카드 스타일 */
    .weather-card {
        background-color: #1e1e2e;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        border: 1px solid #2d2d3f;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    /* 기온 표시 큼직한 네온 텍스트 */
    .temp-display {
        font-size: clamp(3rem, 10vw, 5rem);
        font-weight: 800;
        color: #00f2fe;
        text-shadow: 0 0 15px rgba(0, 242, 254, 0.3);
        margin: 0.5rem 0;
    }

    /* 옷차림 추천 상자 */
    .recommend-box {
        background-color: #2b2b3d;
        border-radius: 15px;
        padding: 1.5rem;
        border-left: 5px solid #00f2fe;
        margin-top: 1rem;
        text-align: left;
    }

    .recommend-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }

    .recommend-text {
        font-size: 1.1rem;
        color: #d0d0e0;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)


# 4. 기온별 옷차림 추천 데이터베이스 (함수)
def get_outfit_recommendation(temp, condition):
    """기온과 날씨 상태에 맞춰 적절한 옷차림을 반환하는 함수"""
    outfit = []
    tip = ""

    # 기온 구간별 기본 옷차림
    if temp >= 28:
        outfit = ["민소매", "반팔티", "반바지", "린넨 옷"]
        tip = "무더운 날씨입니다. 얇고 통풍이 잘 되는 옷을 입으세요!"
    elif 23 <= temp < 28:
        outfit = ["반팔티", "얇은 셔츠", "반바지", "면바지"]
        tip = "자가용이나 실내 에어컨 바람에 대비해 얇은 가디건을 챙기면 좋습니다."
    elif 20 <= temp < 23:
        outfit = ["긴팔티", "가디건", "후드티", "청바지", "슬랙스"]
        tip = "일교차가 클 수 있으니 가벼운 외투를 준비하세요."
    elif 17 <= temp < 20:
        outfit = ["니트", "맨투맨", "가디건", "청바지"]
        tip = "선선한 날씨입니다. 활동하기 좋은 겉옷을 챙기세요."
    elif 12 <= temp < 17:
        outfit = ["자켓", "트렌치코트", "야상", "니트", "청바지"]
        tip = "쌀쌀함을 느낄 수 있는 날씨입니다. 자켓이나 트렌치코트를 추천합니다."
    elif 9 <= temp < 12:
        outfit = ["트렌치코트", "점퍼", "니트", "기모바지"]
        tip = "쌀쌀한 바람이 불어요. 따뜻한 니트나 코트를 입으세요."
    elif 5 <= temp < 9:
        outfit = ["울 코트", "가죽 자켓", "히트텍", "니트", "레깅스"]
        tip = "추운 날씨입니다. 얇은 옷을 여러 겹 레이어드해 입으세요."
    else:
        outfit = ["패딩", "두꺼운 코트", "목도리", "기모 제품", "장갑"]
        tip = "한파 주의! 방한용품과 두꺼운 패딩으로 체온을 유지하세요."

    # 날씨 상태별 추가 팁
    if condition == "비":
        tip += " ☔ 비가 오니 우산과 방수 신발을 챙기세요!"
    elif condition == "눈":
        tip += " ❄️ 눈이 오니 미끄러지지 않는 신발을 신으세요!"
    elif condition == "바람강함":
        tip += " 💨 바람이 강하게 불어 바람막이나 코트가 유용합니다."

    return outfit, tip


# 5. 헤더 구역
st.markdown("<h1 style='text-align: center; color: #ffffff;'>🌤️ 오늘 뭐 입지? 날씨 & 옷차림 추천</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a0a0b0;'>기온과 날씨에 딱 맞는 옷차림을 확인해 보세요!</p>", unsafe_allow_html=True)


# 6. 메인 입력 및 표시 구역
with st.container():
    st.markdown('<div class="weather-card">', unsafe_allow_html=True)

    # 주요 도시 선택 및 날씨 설정
    col1, col2 = st.columns(2)
    
    with col1:
        city = st.selectbox(
            "📍 도시 선택",
            ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "제주"],
            key="selected_city"
        )
    
    with col2:
        weather = st.selectbox(
            "🌤️ 날씨 상태",
            ["맑음", "구름많음", "비", "눈", "바람강함"],
            key="weather_condition"
        )

    # 기온 조절 슬라이더 (-10℃ ~ 35℃)
    temp = st.slider(
        "🌡️ 기온 설정 (℃)",
        min_value=-15,
        max_value=35,
        value=st.session_state.custom_temp,
        key="custom_temp"
    )

    # 날씨 상태별 아이콘 설정
    icon_map = {
        "맑음": "☀️",
        "구름많음": "⛅",
        "비": "🌧️",
        "눈": "❄️",
        "바람강함": "💨"
    }

    # 중앙 대형 기온 디스플레이
    st.markdown(f"""
        <div style="margin-top: 1.5rem;">
            <span style="font-size: 2rem;">{icon_map[weather]} {city}의 날씨</span>
            <div class="temp-display">{temp}°C</div>
        </div>
    """, unsafe_allow_html=True)

    # 옷차림 추천 결과 가져오기
    outfits, tip_message = get_outfit_recommendation(temp, weather)

    # 추천 결과 상자 출력
    st.markdown(f"""
        <div class="recommend-box">
            <div class="recommend-title">👔 추천 옷차림</div>
            <div class="recommend-text">
                <b>주요 아이템:</b> {', '.join(outfits)}
            </div>
            <hr style="border-color: #3d3d52; margin: 0.8rem 0;">
            <div class="recommend-text">
                💡 <b>코디 팁:</b> {tip_message}
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# 7. 빠른 설정 버튼 구역 (계절별 빠른 기온 테스트)
st.markdown("<p style='color: #d0d0e0; font-weight: bold;'>⚡ 계절별 빠른 확인</p>", unsafe_allow_html=True)
q_col1, q_col2, q_col3, q_col4 = st.columns(4)

def set_season(temperature, condition):
    st.session_state.custom_temp = temperature
    st.session_state.weather_condition = condition

with q_col1:
    if st.button("🌸 봄 (15℃)", use_container_width=True):
        set_season(15, "맑음")
        st.rerun()
with q_col2:
    if st.button("☀️ 여름 (30℃)", use_container_width=True):
        set_season(30, "맑음")
        st.rerun()
with q_col3:
    if st.button("🍁 가을 (18℃)", use_container_width=True):
        set_season(18, "구름많음")
        st.rerun()
with q_col4:
    if st.button("❄️ 겨울 (-5℃)", use_container_width=True):
        set_season(-5, "눈")
        st.rerun()
