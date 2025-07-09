import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from PIL import Image, ExifTags
import numpy as np

# 앱 제목
st.title("서울 기준 동적 천체 거리 나이 시각화")

# 이미지 업로드
st.header("이미지 업로드")
uploaded_image = st.file_uploader("천체 이미지를 업로드하세요 (선택 사항, JPG, PNG)", type=["jpg", "jpeg", "png"])

# EXIF 데이터에서 방위각 추출
def get_exif_data(image):
    try:
        exif_data = image._getexif()
        if exif_data is not None:
            for tag, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag, tag)
                if tag_name == "GPSInfo":
                    gps_info = value
                    for gps_tag, gps_value in gps_info.items():
                        gps_tag_name = ExifTags.GPSTAGS.get(gps_tag, gps_tag)
                        if gps_tag_name == "GPSImgDirection":
                            return gps_value[0] / gps_value[1]  # 방위각 (도)
        return None
    except Exception:
        return None

# 이미지 처리 및 방위각 표시
if uploaded_image is not None:
    image = Image.open(uploaded_image)
    st.image(image, caption="업로드된 이미지", use_column_width=True)
    azimuth_data = get_exif_data(image)
    if azimuth_data is not None:
        st.write(f"이미지에서 추출된 방위각: {azimuth_data:.2f}° (참고용, 입력값이 우선)")
    else:
        st.write("이미지에서 방위각 정보를 추출할 수 없습니다.")
else:
    st.write("이미지를 업로드하면 여기에 표시됩니다.")

# 사용자 입력
st.header("천체 위치와 나이 입력")
st.write("서울(위도 37.57°N, 경도 126.98°E)을 기준으로 천체 위치를 입력하세요.")
current_age = st.number_input("현재 나이를 입력하세요 (세):", min_value=0, max_value=120, value=30, step=1)
distance = st.number_input("천체까지의 거리 (광년):", min_value=0.0, value=10.0, step=0.1)
azimuth = st.number_input("방위각 (도, 0°~360°):", min_value=0.0, max_value=360.0, value=26.13, step=0.1)
altitude = st.number_input("고도 (도, -90°~90°):", min_value=-90.0, max_value=90.0, value=42.12, step=0.1)

# 나이 계산
observed_age = max(0, current_age - distance)

# 결과 표시
st.header("결과")
st.write(f"현재 나이: {current_age}세")
st.write(f"천체 위치: 방위각 {azimuth:.2f}°, 고도 {altitude:.2f}°, 거리 {distance} 광년")
st.write(f"{distance} 광년 떨어진 천체에서 관찰되는 당신의 나이: {observed_age}세")

# 나이 비교 시각화
st.header("나이 비교 시각화")
data_age = {
    "상황": ["현재 나이", "관찰된 나이"],
    "나이 (세)": [current_age, observed_age]
}
df_age = pd.DataFrame(data_age)
fig_age = px.bar(df_age, x="상황", y="나이 (세)", title="현재 나이와 천체에서 관찰된 나이 비교",
                 color="상황", color_discrete_sequence=["#636EFA", "#EF553B"])
fig_age.update_layout(width=600, height=400)
st.plotly_chart(fig_age)

# 천체 위치 시각화 (극좌표 플롯)
st.header("천체 위치 시각화 (방위각과 고도)")
fig_pos = go.Figure()
r = 90 - abs(altitude)  # 고도를 반지름으로 변환
fig_pos.add_trace(go.Scatterpolar(
    r=[r],
    theta=[azimuth],
    mode="markers+text",
    name="천체 위치",
    text=[f"방위각: {azimuth:.2f}°, 고도: {altitude:.2f}°"],
    marker=dict(size=10, color="#EF553B")
))
fig_pos.update_layout(
    polar=dict(
        radialaxis=dict(range=[0, 90], visible=True),
        angularaxis=dict(direction="clockwise")
    ),
    showlegend=True,
    width=600,
    height=400
)
st.plotly_chart(fig_pos)

# 설명
st.header("설명")
st.write("""
서울(위도 37.57°N, 경도 126.98°E)을 기준으로 입력한 방위각과 고도에 위치한 천체를 사용합니다.
빛은 유한한 속도로 이동하므로, 입력한 거리(광년)만큼 과거의 당신의 모습을 봅니다.
예를 들어, 10광년 떨어진 천체에서는 당신이 10년 전의 모습(즉, 현재 나이 - 10세)을 보게 됩니다.
업로드한 이미지는 참고용으로 표시되며, EXIF 데이터에서 방위각을 추출할 수 있으면 참고로 보여줍니다.
방위각과 고도는 사용자가 입력한 값이 우선 적용됩니다.
""")
