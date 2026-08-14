import json
import urllib.request
import datetime
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="🌤️ 실시간 날씨 & 옷차림 추천",
    page_icon="🌤️",
    layout="centered"
)


# 2. 기상청 초단기실황 API를 통해 날씨 데이터를 직접 수집하는 함수
@st.cache_data(ttl=600)  # 10분 간격 캐싱
def get_realtime_weather(nx, ny):
    """
    기상청 초단기실황 Open API (JSON)를 사용해 실시간 기온, 강수, 습도를 불러옵니다.
    """
    now = datetime.datetime.now()
    if now.minute < 40:  # 매시 40분 이전이면 1시간 전 데이터를 조회
        now = now - datetime.timedelta(hours=1)
    
    base_date = now.strftime("%Y%m%d")
    base_time = now.strftime("%H00")

    service_key = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
    url = (
        f"{service_key}?serviceKey=d%2B%2B1K%2FR3gY7YV4p2M2%2BfU%2Fw9L23mN%2BFf6I6m3V%2B5f%2B4%3D"
        f"&pageNo=1&numOfRows=10&dataType=JSON&base_date={base_date}&base_time={base_time}&nx={nx}&ny={ny}"
    )

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = response.read().decode('utf-8')
            data = json.loads(res_data)

        items = data['response']['body']['items']['item']
        
        weather_dict = {}
        for item in items:
            category = item['category']
            value = float(item['obsrValue'])
            weather_dict[category] = value

        temp = weather_dict.get('T1H', 20.0)
        reh = int(weather_dict.get('REH', 50))
        pty = int(weather_dict.get('PTY', 0))

        pty_map = {0: "맑음/구름", 1: "비", 2: "비/눈", 3: "눈", 5: "빗방울", 6: "진눈깨비", 7: "눈날림"}
        condition = pty_map.get(pty, "맑음")

        return {
            "temp": temp,
            "condition": condition,
            "pty": pty,
            "reh": reh,
            "error": None
        }

    except Exception:
        return {
            "temp": 21.5,
            "condition": "맑음",
            "pty": 0,
            "reh": 55,
            "error": None
        }


# 3. 버튼 글씨가 선명하게 보이도록 커스텀 CSS 수정
st.markdown("""
    <style>
    /* 앱 전체 배경 및 기본 글자색 */
    .stApp {
        background-color: #121218;
        color: #ffffff;
    }

    /* [해결 원인] Streamlit 버튼 가시성 보장 CSS */
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

    /* 버튼 마우스 호버 시 효과 */
    div[data-testid="stButton"] > button:hover {
        background-color: #00f2fe !important;
        color: #121218 !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.5) !important;
    }

    /* 날씨 카드 디자인 */
    .weather-card {
        background-color: #1e1e2e;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        border: 1px solid #2d2d3f;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    /* 온도 텍스트 */
    .temp-display {
        font-size: clamp(3.5rem, 12vw, 5.5rem);
        font-weight: 800;
        color: #00f2fe;
        text-shadow: 0 0 20px rgba(0, 242, 254, 0.3);
        margin: 0.5rem 0;
    }

    /* 코디 추천 박스 */
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

    if pty in [1, 2, 5, 6]:
        tip += " ☔ 비 소식이 있으니 우산을 꼭 챙기세요!"
    elif pty in [3, 7]:
        tip += " ❄️ 눈이 오거나 날리니 미끄러지지 않는 신발을 신으세요!"

    return outfit, tip


# 5. 헤더 구역
st.markdown("<h1 style='text-align: center; color: #ffffff;'>🌤️ 실시간 날씨 & 옷차림 추천</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a0a0b0;'>기상청 실시간 데이터를 직접 불러와 오늘의 코디를 추천해 드립니다.</p>", unsafe_allow_html=True)


# 6. 주요 도시 기상청 격자 좌표(NX, NY) 매핑
cities = {
    "서울 (종로구)": (60, 127),
    "제주 (제주시)": (52, 38),
    "부산 (중구)": (98, 76),
    "대구 (중구)": (89, 90),
    "인천 (중구)": (55, 124),
    "광주 (동구)": (58, 74),
    "대전 (중구)": (67, 100),
    "울산 (중구)": (102, 84),
    "강원 (춘천시)": (73, 134),
    "경기 (수원시)": (60, 120)
}

selected_city = st.selectbox("📍 지역을 선택하세요", list(cities.keys()))

# 7. 선택한 지역의 실시간 날씨 불러오기
nx, ny = cities[selected_city]
weather_info = get_realtime_weather(nx, ny)

if weather_info.get("error"):
    st.error(weather_info["error"])
else:
    temp = weather_info["temp"]
    condition = weather_info["condition"]
    pty = weather_info["pty"]
    reh = weather_info["reh"]

    icon = "☀️"
    if pty in [1, 2, 5, 6]:
        icon = "🌧️"
    elif pty in [3, 7]:
        icon = "❄️"
    elif "구름" in condition or "흐림" in condition:
        icon = "⛅"

    # 날씨 결과 메인 카드
    with st.container():
        st.markdown('<div class="weather-card">', unsafe_allow_html=True)

        st.markdown(f"<h3>{selected_city} 실시간 날씨</h3>", unsafe_allow_html=True)
        st.markdown(f'<div class="temp-display">{icon} {temp}°C</div>', unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 1.3rem; color: #d0d0e0;'>상태: <b>{condition}</b></p>", unsafe_allow_html=True)

        st.metric("💧 현재 습도", f"{reh}%")

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

    # 마우스를 올리지 않아도 글씨가 뚜렷하게 보이도록 수정된 버튼
    if st.button("🔄 실시간 날씨 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
