import streamlit as st
import pandas as pd

# ==========================================
# 페이지 설정
# ==========================================
st.set_page_config(
    page_title="서울 100년 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

# ==========================================
# 데이터 주소
# ==========================================
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


# ==========================================
# 데이터 불러오기
# ==========================================
@st.cache_data
def load_data():

    df = pd.read_csv(
        DATA_URL,
        encoding="utf-8"
    )

    # 날짜 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"],
        errors="coerce"
    )

    # 숫자형으로 변환할 열
    numeric_columns = [
        "지점",
        "평균기온",
        "최저기온",
        "최고기온"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # 날짜가 없는 행 제거
    df = df.dropna(
        subset=["날짜"]
    )

    # 연도 추가
    df["연도"] = df["날짜"].dt.year

    # ======================================
    # 연도별 연평균 기온 계산
    # ======================================
    yearly = (
        df.dropna(
            subset=["평균기온"]
        )
        .groupby("연도")["평균기온"]
        .mean()
        .reset_index()
    )

    return df, yearly


# ==========================================
# 앱 실행
# ==========================================
try:

    df, yearly = load_data()

    # ======================================
    # 제목
    # ======================================
    st.title("🌡️ 서울의 100년 기온 변화")

    st.write(
        "서울의 기온 데이터를 이용하여 "
        "100년 동안 연평균 기온이 어떻게 변화해 왔는지 살펴봅니다."
    )

    # ======================================
    # 데이터 기본 정보
    # ======================================
    st.subheader("📌 데이터 기본 정보")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "전체 데이터 개수",
            f"{len(df):,}개"
        )

    with col2:
        st.metric(
            "관측 지점",
            f"{df['지점'].nunique():,}개"
        )

    with col3:
        st.metric(
            "시작 연도",
            f"{df['날짜'].dt.year.min()}년"
        )

    with col4:
        st.metric(
            "마지막 연도",
            f"{df['날짜'].dt.year.max()}년"
        )

    # ======================================
    # 원본 데이터 요약통계
    # ======================================
    st.subheader("📊 원본 데이터 요약통계")

    st.write(
        "원본 데이터의 지점, 평균기온, 최저기온, 최고기온에 대한 "
        "요약통계입니다."
    )

    # 사진과 동일하게 지점까지 포함
    summary = df[
        [
            "지점",
            "평균기온",
            "최저기온",
            "최고기온"
        ]
    ].describe()

    # 통계 이름을 한글로 변경
    summary = summary.rename(
        index={
            "count": "개수",
            "mean": "평균",
            "std": "표준편차",
            "min": "최소",
            "25%": "25%",
            "50%": "50% (중앙값)",
            "75%": "75%",
            "max": "최대"
        }
    )

    # 소수점 둘째 자리까지 표시
    summary = summary.round(2)

    # 통계표 표시
    st.dataframe(
        summary,
        use_container_width=True
    )

    # ======================================
    # 연평균 기온 그래프
    # ======================================
    st.subheader("📈 연도별 연평균 기온 변화")

    chart_data = yearly.set_index("연도")

    st.line_chart(
        chart_data,
        y="평균기온",
        x_label="연도",
        y_label="연평균 기온 (℃)",
        use_container_width=True
    )

    # ======================================
    # 주요 기록
    # ======================================
    st.subheader("🔎 주요 기록")

    col1, col2, col3 = st.columns(3)

    # 가장 낮은 연평균 기온
    with col1:

        lowest = yearly.loc[
            yearly["평균기온"].idxmin()
        ]

        st.metric(
            "가장 낮은 연평균 기온",
            f"{lowest['평균기온']:.1f} ℃",
            f"{int(lowest['연도'])}년"
        )

    # 가장 높은 연평균 기온
    with col2:

        highest = yearly.loc[
            yearly["평균기온"].idxmax()
        ]

        st.metric(
            "가장 높은 연평균 기온",
            f"{highest['평균기온']:.1f} ℃",
            f"{int(highest['연도'])}년"
        )

    # 처음과 마지막 연도의 차이
    with col3:

        first_temp = yearly.iloc[0]["평균기온"]
        last_temp = yearly.iloc[-1]["평균기온"]

        change = last_temp - first_temp

        st.metric(
            "처음과 마지막 연도의 차이",
            f"{change:+.1f} ℃"
        )

    # ======================================
    # 연도별 데이터
    # ======================================
    with st.expander("📋 연도별 평균기온 데이터 보기"):

        display_data = yearly.copy()

        display_data["평균기온"] = display_data[
            "평균기온"
        ].round(2)

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )

    # ======================================
    # 원본 데이터
    # ======================================
    with st.expander("📄 원본 데이터 일부 보기"):

        st.dataframe(
            df.head(100),
            use_container_width=True,
            hide_index=True
        )


# ==========================================
# 오류 처리
# ==========================================
except Exception as e:

    st.error(
        "데이터를 불러오는 중 문제가 발생했습니다."
    )

    st.write(
        f"오류 내용: {e}"
    )
