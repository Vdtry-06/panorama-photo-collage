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
tab1, tab2, tab3 = st.tabs(["Upload Ảnh", "Phân tích", "Kết quả"])

with tab1:
    st.header("Upload ảnh")
    
    uploaded_files = st.file_uploader(
        "Chọn 2-3 ảnh (JPG, PNG)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        help="Upload ảnh từ trái sang phải"
    )
    
    save_path = "/app/data"
    os.makedirs(save_path, exist_ok=True)
    
    if uploaded_files and len(uploaded_files) >= 2:
        st.success(f"Đã upload {len(uploaded_files)} ảnh")
        
        cols = st.columns(len(uploaded_files))
        for idx, (col, file) in enumerate(zip(cols, uploaded_files)):
            with col:
                image = Image.open(file)
                # st.image(image, caption=f"Ảnh {idx+1}", use_container_width=True)
                st.image(image, caption=f"Ảnh {idx+1}")
                
                save_file_path = os.path.join(save_path, file.name)
                image.save(save_file_path)
    elif uploaded_files:
        st.warning("Cần ít nhất 2 ảnh để ghép panorama")

with tab2:
    st.header("Phân tích Keypoints và Matches")
    
    if uploaded_files and len(uploaded_files) >= 2:
        # Load images
        images = [load_image(f) for f in uploaded_files]
        
        # Khởi tạo stitcher
        stitcher = PanoramaStitcher(
            n_features=n_features,
            ratio_threshold=ratio_threshold,
            ransac_threshold=ransac_threshold
        )
        
        # Phân tích từng cặp ảnh
        for i in range(len(images) - 1):
            st.subheader(f"Cặp ảnh {i+1} - {i+2}")
            
            # Detect keypoints
            kp1, desc1 = stitcher.detect_and_describe(images[i])
            kp2, desc2 = stitcher.detect_and_describe(images[i+1])
            
            col1, col2 = st.columns(2)
            
            with col1:
                if show_keypoints:
                    img_kp1 = draw_keypoints(images[i].copy(), kp1)
                    st.image(bgr_to_rgb(img_kp1), caption=f"Ảnh {i+1}: {len(kp1)} keypoints")
                else:
                    st.image(bgr_to_rgb(images[i]), caption=f"Ảnh {i+1}")
                    
            with col2:
                if show_keypoints:
                    img_kp2 = draw_keypoints(images[i+1].copy(), kp2)
                    st.image(bgr_to_rgb(img_kp2), caption=f"Ảnh {i+2}: {len(kp2)} keypoints")
                else:
                    st.image(bgr_to_rgb(images[i+1]), caption=f"Ảnh {i+2}")
            
            # Match keypoints
            if show_matches:
                matches = stitcher.match_keypoints(desc1, desc2)
                matches_img = cv2.drawMatches(
                    images[i], kp1, 
                    images[i+1], kp2, 
                    matches, None,
                    flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
                )
                st.image(bgr_to_rgb(matches_img), caption=f"Matches: {len(matches)}")
            
            # Thống kê
            st.markdown(f"""
            <div class='info-box'>
            <b>Thống kê:</b><br>
            • Keypoints ảnh {i+1}: {len(kp1)}<br>
            • Keypoints ảnh {i+2}: {len(kp2)}<br>
            • Số matches: {len(stitcher.match_keypoints(desc1, desc2))}
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()
    else:
        st.info("Vui lòng upload ảnh ở tab 'Upload Ảnh'")

with tab3:
    st.header("Kết quả Panorama")
    
    if uploaded_files and len(uploaded_files) >= 2:
        if st.button("Ghép ảnh Panorama", type="primary"):
            with st.spinner("Đang xử lý..."):
                try:
                    # Load images
                    images = [load_image(f) for f in uploaded_files]
                    
                    # Khởi tạo stitcher
                    stitcher = PanoramaStitcher(
                        n_features=n_features,
                        ratio_threshold=ratio_threshold,
                        ransac_threshold=ransac_threshold
                    )
                    
                    # Ghép ảnh
                    if len(images) == 2:
                        panorama, info = stitcher.stitch_pair(images[0], images[1])
                        infos = [info]
                    else:
                        panorama, infos = stitcher.stitch_multiple(images)
                    
                    # Hiển thị kết quả
                    st.success("Ghép ảnh thành công!")
                    
                    # Crop vùng đen
                    gray = cv2.cvtColor(panorama, cv2.COLOR_BGR2GRAY)
                    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
                    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    if contours:
                        x, y, w, h = cv2.boundingRect(contours[0])
                        panorama_cropped = panorama[y:y+h, x:x+w]
                    else:
                        panorama_cropped = panorama
                    
                    # Hiển thị
                    st.image(bgr_to_rgb(panorama_cropped), caption="Ảnh Panorama", width=None)
                    
                    # Thống kê tổng hợp
                    st.markdown("###Thống kê chi tiết")
                    for idx, info in enumerate(infos):
                        st.markdown(f"""
                        <div class='info-box'>
                        <b>Cặp ảnh {idx+1} - {idx+2}:</b><br>
                        • Keypoints: {info['keypoints1']} - {info['keypoints2']}<br>
                        • Matches: {info['matches']}<br>
                        • Inliers: {info['inliers']}<br>
                        • Inlier ratio: {info['inliers']/info['matches']*100:.1f}%
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Convert to PIL Image
                    panorama_rgb = cv2.cvtColor(panorama_cropped, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(panorama_rgb)
                    
                    # Save to bytes
                    buf = io.BytesIO()
                    pil_img.save(buf, format='PNG')
                    byte_img = buf.getvalue()
                    
                    st.download_button(
                        label="Tải ảnh Panorama",
                        data=byte_img,
                        file_name="panorama.png",
                        mime="image/png"
                    )
                    
                except Exception as e:
                    st.error(f"Lỗi: {str(e)}")
                    st.info("Thử điều chỉnh các tham số hoặc sử dụng ảnh khác")
    else:
        st.info("Vui lòng upload ảnh ở tab 'Upload Ảnh'")


## Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px'>
<b>Panorama Stitching Tool</b> - Đề tài Xử lý ảnh số<br>
Sử dụng SIFT Algorithm cho phát hiện và mô tả keypoints
</div>
""", unsafe_allow_html=True)