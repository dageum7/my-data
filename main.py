import pandas as pd
import streamlit as st

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"

st.set_page_config(
    page_title="서울 연평균 기온 변화",
    page_icon="🌡️",
    layout="wide",
)

st.title("서울 연평균 기온 변화")
st.write("서울의 일별 기온 데이터를 이용해 연도별 평균기온의 변화를 살펴봅니다.")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜를 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

    # 평균기온을 숫자형으로 변환
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")

    # 분석에 필요한 데이터만 남김
    df = df.dropna(subset=["날짜", "평균기온"]).copy()

    # 연도 추출
    df["연도"] = df["날짜"].dt.year

    return df


df = load_data()

# 연도별 평균기온 계산
yearly = (
    df.groupby("연도", as_index=False)["평균기온"]
    .mean()
    .rename(columns={"평균기온": "연평균기온"})
    .sort_values("연도")
)

if yearly.empty:
    st.error("기온 데이터를 불러오지 못했습니다.")
    st.stop()

# 기본 통계
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("분석 시작 연도", f"{yearly['연도'].min()}년")

with col2:
    st.metric("분석 종료 연도", f"{yearly['연도'].max()}년")

with col3:
    st.metric("분석 연수", f"{len(yearly)}년")

st.subheader("연도별 연평균 기온")

chart_data = yearly.set_index("연도")

st.line_chart(
    chart_data,
    y="연평균기온",
    x_label="연도",
    y_label="연평균 기온(℃)",
    height=500,
)

st.caption(
    "※ 연평균 기온은 해당 연도의 일별 평균기온을 산술평균한 값입니다."
)

with st.expander("연도별 데이터 보기"):
    display_df = yearly.copy()
    display_df["연평균기온"] = display_df["연평균기온"].round(2)
    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
    )
