import json
import urllib.request
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="🌤️ 실시간 날씨 & 옷차림 추천",
    page_icon="🌤️",
    layout="centered"
)


# 2. Open-Meteo API를 사용하여 각 도시의 실시간 위도/경도 기반 날씨 수집 (API Key 필요 없음)
@st.cache_data(ttl=600)  # 10분 간격 캐싱
def get_realtime_weather(lat, lon):
    """
    도시별 위도(lat)와 경도(lon)로 실시간 기온, 습도, 날씨 상태 코드를 정확하게 불러옵니다.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code&timezone=Asia%2FTokyo"

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = response.read().decode('utf-8')
            data = json.loads(res_data)

        current = data['current']
        temp = round(current['temperature_2m'], 1)
        reh = int(current['relative_humidity_2m'])
        w_code = int(current['weather_code'])

        # WMO 날씨 코드 해석
        condition = "맑음"
        pty = 0

        if w_code in [1, 2, 3]:
            condition = "구름많음/흐림"
        elif w_code in [45, 48]:
            condition = "안개"
        elif w_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
            condition = "비"
            pty = 1
        elif w_code in [71, 73, 75, 77, 85, 86]:
            condition = "눈"
            pty = 3
        elif w_code in [95, 96, 99]:
            condition = "뇌우"
            pty = 1

        return {
            "temp": temp,
            "condition": condition,
            "pty": pty,
            "reh": reh,
            "error": None
        }

    except Exception as e:
        return {"error": f"날씨 정보를 불러오는 중 오류가 발생했습니다: {e}"}


# 3. 커스텀 CSS 적용 (글자 가시성 및 다크 테마)
st.markdown("""
    <style>
    /* 전체 배경 */
    .stApp {
        background-color: #121218;
        color: #ffffff;
    }

    /* Streamlit 기본 버튼 스타일 */
    div[data-testid="stButton"] > button {
        background-color: #2b2b3d !important;
        color: #00f2fe !important;
        border: 1px solid #00f2fe !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        padding: 0.6rem 1rem !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
    }

    div[data-testid="stButton"] > button:hover {
        background-color: #00f2fe !important;
        color: #121218 !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.5) !important;
    }

    /* 카드 디자인 */
    .weather-card {
        background-color: #1e1e2e;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        border: 1px solid #2d2d3f;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    /* 온점 큰 글씨 */
    .temp-display {
        font-size: clamp(3.5rem, 12vw, 5.5rem);
        font-weight: 800;
        color: #00f2fe;
        text-shadow: 0 0 20px rgba(0, 242, 254, 0.3);
        margin: 0.5rem 0;
    }

    /* 정보 배지 */
    .info-badge {
        background-color: #2b2b3d;
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
        display: inline-block;
        margin: 0.5rem;
        border: 1px solid #3d3d52;
    }

    .info-label {
        font-size: 0.95rem;
        color: #a0a0b0;
        margin-bottom: 0.2rem;
    }

    .info-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ffffff;
    }

    /* 추천 상자 */
    .recommend-box {
        background-color: #2b2b3d;
        border-radius: 15px;
        padding: 1.5rem;
        border-left: 5px solid #00f2fe;
        margin-top: 1.5rem;
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


# 4. 기온별 옷차림 추천 알고리즘
def get_outfit_recommendation(temp, pty):
    outfit = []
    tip = ""

    if temp >= 28:
        outfit = ["민소매", "반팔티", "반바지", "린넨 의류"]
        tip = "무더운 날씨입니다. 통풍이 잘 되는 얇은 옷을 입으세요."
    elif 23 <= temp < 28:
        outfit = ["반팔티", "얇은 셔츠", "반바지", "면바지"]
        tip = "에어컨 바람에 대비해 얇은 가디건을 챙기면 좋습니다."
    elif 20 <= temp < 23:
        outfit = ["긴팔티", "가디건", "후드티", "청바지", "슬랙스"]
        tip = "일교차가 클 수 있으니 가벼운 겉옷을 준비하세요."
    elif 17 <= temp < 20:
        outfit = ["니트", "맨투맨", "가디건", "청바지"]
        tip = "선선한 날씨입니다. 활동하기 좋은 겉옷을 추천합니다."
    elif 12 <= temp < 17:
        outfit = ["자켓", "트렌치코트", "야상", "니트", "청바지"]
        tip = "쌀쌀함이 느껴질 수 있어 자켓이나 코트가 적합합니다."
    elif 9 <= temp < 12:
        outfit = ["점퍼", "트렌치코트", "두꺼운 니트", "기모 바지"]
        tip = "바람이 차가울 수 있으니 따뜻하게 입으세요."
    elif 5 <= temp < 9:
        outfit = ["울 코트", "가죽 자켓", "히트텍", "니트"]
        tip = "추운 날씨입니다. 얇은 옷을 여러 겹 겹쳐 입으세요."
    else:
        outfit = ["두꺼운 패딩", "코트", "목도리", "기모 의류", "장갑"]
        tip = "한파 주의! 방한 용품과 두꺼운 겉옷을 꼭 챙기세요."

    if pty == 1:
        tip += " ☔ 비 소식이 있으니 우산을 꼭 챙기세요!"
    elif pty == 3:
        tip += " ❄️ 눈 소식이 있으니 미끄러지지 않는 신발을 신으세요!"

    return outfit, tip


# 5. 헤더 구역
st.markdown("<h1 style='text-align: center; color: #ffffff;'>🌤️ 실시간 날씨 & 옷차림 추천</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a0a0b0;'>각 지역의 실시간 기온과 습도를 분석하여 옷차림을 안내합니다.</p>", unsafe_allow_html=True)


# 6. 주요 도시 위도(Latitude) 및 경도(Longitude) 정확한 좌표값
cities = {
    "서울": (37.5665, 126.9780),
    "제주": (33.4996, 126.5312),
    "부산": (35.1796, 129.0756),
    "대구": (35.8714, 128.6014),
    "인천": (37.4563, 126.7052),
    "광주": (35.1595, 126.8526),
    "대전": (36.3504, 127.3845),
    "울산": (35.5384, 129.3114),
    "춘천 (강원)": (37.8813, 127.7298),
    "수원 (경기)": (37.2636, 127.0286)
}

selected_city = st.selectbox("📍 지역을 선택하세요", list(cities.keys()))

# 7. 선택한 도시의 실시간 날씨 불러오기
lat, lon = cities[selected_city]
weather_info = get_realtime_weather(lat, lon)

if weather_info.get("error"):
    st.error(weather_info["error"])
else:
    temp = weather_info["temp"]
    condition = weather_info["condition"]
    pty = weather_info["pty"]
    reh = weather_info["reh"]

    # ไอ콘 설정
    icon = "☀️"
    if pty == 1:
        icon = "🌧️"
    elif pty == 3:
        icon = "❄️"
    elif "구름" in condition or "흐림" in condition:
        icon = "⛅"

    # 날씨 결과 메인 카드
    with st.container():
        st.markdown('<div class="weather-card">', unsafe_allow_html=True)

        st.markdown(f"<h3>{selected_city} 실시간 날씨</h3>", unsafe_allow_html=True)
        st.markdown(f'<div class="temp-display">{icon} {temp}°C</div>', unsafe_allow_html=True)

        st.markdown(f"""
            <div style="margin: 1rem 0;">
                <div class="info-badge">
                    <div class="info-label">🌤️ 날씨 상태</div>
                    <div class="info-value">{condition}</div>
                </div>
                <div class="info-badge">
                    <div class="info-label">💧 현재 습도</div>
                    <div class="info-value" style="color: #00f2fe;">{reh}%</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 옷차림 추천
        outfits, tip_message = get_outfit_recommendation(temp, pty)

        st.markdown(f"""
            <div class="recommend-box">
                <div class="recommend-title">👔 오늘 추천 옷차림</div>
                <div class="recommend-text">
                    <b>추천 아이템:</b> {', '.join(outfits)}
                </div>
                <hr style="border-color: #3d3d52; margin: 0.8rem 0;">
                <div class="recommend-text">
                    💡 <b>코디 팁:</b> {tip_message}
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # 실시간 날씨 새로고침 버튼
    if st.button("🔄 실시간 날씨 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
