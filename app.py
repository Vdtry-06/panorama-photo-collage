"""
Panorama Stitching Tool - Streamlit App
Giao diện web để ghép ảnh panorama
"""

import streamlit as st

## Cấu hình trang
st.set_page_config(
    page_title="Panorama Stitching Tool",
    page_icon="",
    layout="wide"
)

## Header
st.markdown("<h1 class='main-header'>Panorama Stitching Tool</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center'>Ghép ảnh Panorama sử dụng SIFT Algorithm</p>", unsafe_allow_html=True)

## Body


## Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px'>
<b>Panorama Stitching Tool</b> - Đề tài Xử lý ảnh số<br>
Sử dụng SIFT Algorithm cho phát hiện và mô tả keypoints
</div>
""", unsafe_allow_html=True)