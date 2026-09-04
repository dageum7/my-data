import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="서울 100년 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

# 데이터 주소
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


@st.cache_data
def load_data():
    # 원본 데이터 불러오기
    df = pd.read_csv(DATA_URL, encoding="utf-8")

    # 날짜 변환
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

    # 기온 열 숫자형 변환
    temp_columns = ["평균기온", "최저기온", "최고기온"]

    for column in temp_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # 날짜가 정상적인 행만 사용
    df = df.dropna(subset=["날짜"])

    # 연도 추출
    df["연도"] = df["날짜"].dt.year

    # 연평균 기온 계산
    yearly = (
        df.dropna(subset=["평균기온"])
        .groupby("연도")["평균기온"]
        .mean()
        .reset_index()
    )

    return df, yearly


try:
    # 데이터 불러오기
    df, yearly = load_data()

    # -----------------------------
    # 제목
    # -----------------------------
    st.title("🌡️ 서울의 100년 기온 변화")

    st.write(
        "서울의 일별 기온 데이터를 이용해 "
        "연평균 기온의 장기적인 변화를 살펴봅니다."
    )

    # -----------------------------
    # 데이터 기간
    # -----------------------------
    start_year = int(yearly["연도"].min())
    end_year = int(yearly["연도"].max())

    st.info(
        f"📅 분석 기간: **{start_year}년 ~ {end_year}년**  |  "
        f"연평균 기온을 계산할 수 있는 연도: **{len(yearly)}개**"
    )

    # -----------------------------
    # 원본 데이터 요약
    # -----------------------------
    st.subheader("📊 원본 데이터 요약통계")

    st.write(
        "원본 일별 데이터에서 평균기온·최저기온·최고기온의 "
        "개수, 평균, 최소값, 사분위수, 최대값을 확인할 수 있습니다."
    )

    # 요약통계 계산
   summary = df[
    ["평균기온", "최저기온", "최고기온"]
].describe().T

# 행과 열을 서로 바꾸기
summary = summary.T

    # 보기 좋은 한글 이름으로 변경
    summary = summary.rename(
        columns={
            "count": "개수",
            "mean": "평균",
            "std": "표준편차",
            "min": "최소",
            "25%": "25% 값",
            "50%": "중앙값",
            "75%": "75% 값",
            "max": "최대"
        },
        index={
            "평균기온": "평균기온 (℃)",
            "최저기온": "최저기온 (℃)",
            "최고기온": "최고기온 (℃)"
        }
    )

    # 숫자 표시 형식
    summary["개수"] = summary["개수"].astype(int)
    summary = summary.round(2)

    st.dataframe(
        summary,
        use_container_width=True
    )

    # -----------------------------
    # 연평균 기온 그래프
    # -----------------------------
    st.subheader("📈 연도별 평균기온 변화")

    chart_data = yearly.set_index("연도")

    st.line_chart(
        chart_data,
        y="평균기온",
        x_label="연도",
        y_label="연평균 기온 (℃)",
        use_container_width=True
    )

    # -----------------------------
    # 주요 통계
    # -----------------------------
    st.subheader("🔎 주요 기록")

    col1, col2, col3 = st.columns(3)

    with col1:
        lowest = yearly.loc[yearly["평균기온"].idxmin()]

        st.metric(
            "가장 낮은 연평균 기온",
            f"{lowest['평균기온']:.1f} ℃",
            f"{int(lowest['연도'])}년"
        )

    with col2:
        highest = yearly.loc[yearly["평균기온"].idxmax()]

        st.metric(
            "가장 높은 연평균 기온",
            f"{highest['평균기온']:.1f} ℃",
            f"{int(highest['연도'])}년"
        )

    with col3:
        first_temp = yearly.iloc[0]["평균기온"]
        last_temp = yearly.iloc[-1]["평균기온"]
        change = last_temp - first_temp

        st.metric(
            "처음과 마지막 연도의 차이",
            f"{change:+.1f} ℃"
        )

    # -----------------------------
    # 연도별 데이터
    # -----------------------------
    with st.expander("📋 연도별 평균기온 데이터 보기"):
        display_data = yearly.copy()
        display_data["평균기온"] = display_data["평균기온"].round(2)

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )

    # -----------------------------
    # 원본 데이터
    # -----------------------------
    with st.expander("📄 원본 데이터 일부 보기"):
        st.dataframe(
            df.head(100),
            use_container_width=True,
            hide_index=True
        )

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.write(f"오류 내용: {e}")
