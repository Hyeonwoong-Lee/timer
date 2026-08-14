import urllib.request
import xml.etree.ElementTree as ET
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="🌤️ 실시간 날씨 & 옷차림 추천",
    page_icon="🌤️",
    layout="centered"
)


# 2. 기상청 RSS에서 실시간 날씨 정보를 가져오는 함수 (표준 라이브러리만 사용)
@st.cache_data(ttl=600)  # 10분간 캐시를 유지하여 빠른 응답 제공
def get_realtime_weather(rss_code):
    """
    기상청 동네예보 RSS URL에서 최신 날씨(기온, 날씨 상태)를 가져옵니다.
    """
    url = f"http://www.kma.go.kr/wid/queryDFSRSS.jsp?zone={rss_code}"
    
    try:
        # URL에서 데이터 요청 및 읽기
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()

        # XML 파싱
        root = ET.fromstring(xml_data)
        
        # 가장 최근 예보 데이터(첫 번째 <data> 태그) 추출
        data = root.find(".//body/data")
        
        temp = float(data.find("temp").text)      # 현재 기온 (℃)
        wf_kor = data.find("wfKor").text          # 날씨 상태 (예: 맑음, 구름 많음, 흐림, 비 등)
        pop = int(data.find("pop").text)          # 강수 확률 (%)
        reh = int(data.find("reh").text)          # 습도 (%)

        return {
            "temp": temp,
            "condition": wf_kor,
            "pop": pop,
            "reh": reh,
            "error": None
        }
    except Exception as e:
        return {"error": f"날씨 정보를 불러오는 데 실패했습니다: {e}"}


# 3. 다크 테마 커스텀 CSS 스타일 적용
st.markdown("""
    <style>
    .stApp {
        background-color: #121218;
        color: #ffffff;
    }
    
    /* 카드 컨테이너 */
    .weather-card {
        background-color: #1e1e2e;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        border: 1px solid #2d2d3f;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    /* 실시간 기온 큼직한 텍스트 */
    .temp-display {
        font-size: clamp(3.5rem, 12vw, 5.5rem);
        font-weight: 800;
        color: #00f2fe;
        text-shadow: 0 0 20px rgba(0, 242, 254, 0.3);
        margin: 0.5rem 0;
    }

    /* 옷차림 추천 정보 상자 */
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


# 4. 기온별 옷차림 알고리즘
def get_outfit_recommendation(temp, condition, pop):
    outfit = []
    tip = ""

    # 기온별 기본 의상 선택
    if temp >= 28:
        outfit = ["민소매", "반팔티", "반바지", "린넨 의류"]
        tip = "무더운 날씨입니다. 통풍이 잘 되고 얇은 옷을 입으세요."
    elif 23 <= temp < 28:
        outfit = ["반팔티", "얇은 셔츠", "반바지", "면바지"]
        tip = "실내 에어컨 바람에 대비해 얇은 가디건을 챙기면 좋습니다."
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

    # 비/눈 및 강수확률 조건 반영
    if "비" in condition or pop >= 50:
        tip += " ☔ 비 소식이 있거나 확률이 높으니 우산을 꼭 챙기세요!"
    elif "눈" in condition:
        tip += " ❄️ 눈 소식이 있으니 미끄럽지 않은 신발을 신으세요!"

    return outfit, tip


# 5. 헤더 구역
st.markdown("<h1 style='text-align: center; color: #ffffff;'>🌤️ 실시간 날씨 & 옷차림 추천</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a0a0b0;'>기상청 실시간 데이터를 직접 불러와 오늘의 코디를 추천해 드립니다.</p>", unsafe_allow_html=True)


# 6. 지역 선택 정보 (기상청 행정구역 코드 매핑)
city_codes = {
    "서울 (종로구)": "1111051500",
    "부산 (중구)": "2611051000",
    "대구 (중구)": "2711051700",
    "인천 (중구)": "2811051000",
    "광주 (동구)": "2911051000",
    "대전 (중구)": "3011051000",
    "울산 (중구)": "3111051000",
    "제주 (제주시)": "5011051000",
    "강원 (춘천시)": "4211051000",
    "경기 (수원시)": "4111156000"
}

selected_city = st.selectbox("📍 지역을 선택하세요", list(city_codes.keys()))

# 7. 선택한 지역의 실시간 날씨 불러오기
rss_code = city_codes[selected_city]
weather_info = get_realtime_weather(rss_code)

if weather_info.get("error"):
    st.error(weather_info["error"])
else:
    temp = weather_info["temp"]
    condition = weather_info["condition"]
    pop = weather_info["pop"]
    reh = weather_info["reh"]

    # 날씨 아이콘 매핑
    icon = "☀️"
    if "구름" in condition:
        icon = "⛅"
    elif "흐림" in condition:
        icon = "☁️"
    elif "비" in condition:
        icon = "🌧️"
    elif "눈" in condition:
        icon = "❄️"

    # 날씨 결과 메인 카드
    with st.container():
        st.markdown('<div class="weather-card">', unsafe_allow_html=True)

        st.markdown(f"<h3>{selected_city} 실시간 날씨</h3>", unsafe_allow_html=True)
        st.markdown(f'<div class="temp-display">{icon} {temp}°C</div>', unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 1.3rem; color: #d0d0e0;'><b>{condition}</b></p>", unsafe_allow_html=True)

        # 수치 요약 정보 (강수확률, 습도)
        col1, col2 = st.columns(2)
        col1.metric("🌧️ 강수 확률", f"{pop}%")
        col2.metric("💧 현재 습도", f"{reh}%")

        # 옷차림 추천
        outfits, tip_message = get_outfit_recommendation(temp, condition, pop)

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

    # 새로고침 버튼
    if st.button("🔄 실시간 날씨 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
