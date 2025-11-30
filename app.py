"""
Panorama Stitching Tool - Streamlit App
Giao diện web để ghép ảnh panorama
"""

import os
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
from panorama_stitcher import PanoramaStitcher, draw_keypoints

## Cấu hình trang
st.set_page_config(
    page_title="Panorama Stitching Tool",
    page_icon="",
    layout="wide"
)

## CSS tùy chỉnh
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        padding: 20px;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def load_image(uploaded_file):
    """Load và convert ảnh từ uploaded file"""
    image = Image.open(uploaded_file)
    image_array = np.array(image)
    
    if len(image_array.shape) == 3:
        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
    return image_array

def bgr_to_rgb(image):
    """Convert BGR to RGB cho hiển thị"""
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image

## Header
st.markdown("<h1 class='main-header'>Panorama Stitching Tool</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center'>Ghép ảnh Panorama sử dụng SIFT Algorithm</p>", unsafe_allow_html=True)

## Sidebar - Cấu hình
st.sidebar.header("Cấu hình")

n_features = st.sidebar.slider(
    "Số lượng keypoints",
    min_value=100,
    max_value=2000,
    value=500,
    step=100,
    help="Số lượng keypoints tối đa SIFT sẽ phát hiện"
)

ratio_threshold = st.sidebar.slider(
    "Lowe's ratio threshold",
    min_value=0.5,
    max_value=0.9,
    value=0.75,
    step=0.05,
    help="Ngưỡng để lọc matches tốt (thấp hơn = nghiêm ngặt hơn)"
)

ransac_threshold = st.sidebar.slider(
    "RANSAC threshold (pixels)",
    min_value=1.0,
    max_value=10.0,
    value=4.0,
    step=0.5,
    help="Ngưỡng RANSAC để loại bỏ outliers"
)

show_keypoints = st.sidebar.checkbox("Hiển thị keypoints", value=True)
show_matches = st.sidebar.checkbox("Hiển thị matches", value=True)

## Info box
with st.sidebar.expander("Hướng dẫn sử dụng"):
    st.markdown("""
    **Các bước thực hiện:**
    1. Upload 2-3 ảnh có vùng chồng lắp
    2. Ảnh nên được sắp xếp từ trái sang phải
    3. Điều chỉnh các tham số nếu cần
    4. Nhấn "Ghép ảnh Panorama"
    5. Xem kết quả và tải về
    
    **Lưu ý:**
    - Ảnh nên có vùng chồng lắp 30-50%
    - Chất lượng ảnh tốt sẽ cho kết quả tốt hơn
    - Tránh ảnh bị mờ hoặc thiếu sáng
    """)

## Body


## Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px'>
<b>Panorama Stitching Tool</b> - Đề tài Xử lý ảnh số<br>
Sử dụng SIFT Algorithm cho phát hiện và mô tả keypoints
</div>
""", unsafe_allow_html=True)