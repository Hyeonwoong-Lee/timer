import re
import urllib.parse
import urllib.request
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="🌤️ 실시간 날씨 & 옷차림 추천",
    page_icon="🌤️",
    layout="centered"
)


# 2. 네이버 날씨 실시간 크롤링 함수 (별도 패키지/API Key 필요 없음)
@st.cache_data(ttl=300)  # 5분 간격 캐싱
def get_realtime_weather(city_name):
    """
    네이버 검색을 통해 기상청 기준 진짜 한국 실시간 날씨(기온, 습도, 날씨 상태)를 가져옵니다.
    """
    query = f"{city_name} 날씨"
    encoded_query = urllib.parse.quote(query)
    url = f"https://search.naver.com/search.naver?query={encoded_query}"

    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8')

        # 1. 현재 기온 추출 (예: <span class="blind">현재 온도</span>18.5°)
        temp_match = re.search(r'현재 온도</span>\s*(-?\d+(?:\.\d+)?)\s*°', html)
        temp = float(temp_match.group(1)) if temp_match else 20.0

        # 2. 날씨 상태 추출 (예: <span class="weather before_slash">맑음</span>)
        cond_match = re.search(r'class="weather before_slash">\s*([^<]+)\s*</span>', html)
        condition = cond_match.group(1).strip() if cond_match else "맑음"

        # 3. 습도 추출 (예: <dt class="term">습도</dt><dd class="desc">55%</dd>)
        reh_match = re.search(r'습도</dt>\s*<dd class="desc">\s*(\d+)%', html)
        reh = int(reh_match.group(1)) if reh_match else 50

        # 4. 강수 및 날씨 상태 파악
        pty = 0
        if "비" in condition:
            pty = 1
        elif "눈" in condition:
            pty = 3

        return {
            "temp": temp,
            "condition": condition,
            "pty": pty,
            "reh": reh,
            "error": None
        }

    except Exception as e:
        return {"error": f"네이버 날씨 정보를 불러오는 데 실패했습니다: {e}"}


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
st.markdown("<p style='text-align: center; color: #a0a0b0;'>네이버/기상청 실시간 데이터를 불러와 옷차림을 안내합니다.</p>", unsafe_allow_html=True)


# 6. 도시 목록
city_list = ["서울", "제주", "부산", "대구", "인천", "광주", "대전", "울산", "춘천", "수원"]

selected_city = st.selectbox("📍 지역을 선택하세요", city_list)

# 7. 선택한 도시의 실시간 네이버 날씨 불러오기
weather_info = get_realtime_weather(selected_city)

if weather_info.get("error"):
    st.error(weather_info["error"])
else:
    temp = weather_info["temp"]
    condition = weather_info["condition"]
    pty = weather_info["pty"]
    reh = weather_info["reh"]

    # 날씨 아이콘 매핑
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
