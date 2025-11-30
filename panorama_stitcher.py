import cv2
import numpy as np
from typing import List, Tuple, Optional

class PanoramaStitcher:
    """Class chính để ghép ảnh panorama"""
    
    def __init__(self, 
                 n_features: int = 500,
                 ratio_threshold: float = 0.75,
                 ransac_threshold: float = 4.0):
        
        self.n_features = n_features
        self.ratio_threshold = ratio_threshold
        self.ransac_threshold = ransac_threshold
        
        self.sift = cv2.SIFT_create(nfeatures=n_features)
        
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        self.matcher = cv2.FlannBasedMatcher(index_params, search_params)
        
    def detect_and_describe(self, image: np.ndarray) -> Tuple[List, np.ndarray]:
        """
        Phát hiện keypoints và tính descriptor bằng SIFT
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        keypoints, descriptors = self.sift.detectAndCompute(gray, None)
        
        return keypoints, descriptors
    
    def match_keypoints(self, 
                       desc1: np.ndarray, 
                       desc2: np.ndarray) -> List[cv2.DMatch]:
        """
        Match keypoints giữa 2 ảnh sử dụng KNN và Lowe's ratio test
        """
        matches = self.matcher.knnMatch(desc1, desc2, k=2)
        
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < self.ratio_threshold * n.distance:
                    good_matches.append(m)
                    
        return good_matches

    
    def find_homography(self,
                       kp1: List,
                       kp2: List,
                       matches: List[cv2.DMatch]) -> Tuple[Optional[np.ndarray], np.ndarray]:
        """
        Tính ma trận Homography sử dụng RANSAC
        """
        if len(matches) < 4:
            return None, None
            
        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        
        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, self.ransac_threshold)
        
        return H, mask
    
    def warp_images(self, 
                   img1: np.ndarray, 
                   img2: np.ndarray, 
                   H: np.ndarray) -> np.ndarray:
        """
        Warp và blend 2 ảnh
        """
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        
        corners1 = np.float32([[0, 0], [0, h1], [w1, h1], [w1, 0]]).reshape(-1, 1, 2)
        corners2 = np.float32([[0, 0], [0, h2], [w2, h2], [w2, 0]]).reshape(-1, 1, 2)
        
        corners1_transformed = cv2.perspectiveTransform(corners1, H)
        
        all_corners = np.concatenate((corners2, corners1_transformed), axis=0)
        
        [x_min, y_min] = np.int32(all_corners.min(axis=0).ravel() - 0.5)
        [x_max, y_max] = np.int32(all_corners.max(axis=0).ravel() + 0.5)
        
        translation = np.array([[1, 0, -x_min],
                               [0, 1, -y_min],
                               [0, 0, 1]])
        
        panorama = cv2.warpPerspective(img1, translation @ H, 
                                      (x_max - x_min, y_max - y_min))
        
        panorama[-y_min:h2 + (-y_min), -x_min:w2 + (-x_min)] = img2
        
        return panorama
    
    def stitch_pair(self, 
                   img1: np.ndarray, 
                   img2: np.ndarray,
                   show_matches: bool = False) -> Tuple[np.ndarray, dict]:
        """
        Ghép 2 ảnh thành panorama
        """
        kp1, desc1 = self.detect_and_describe(img1)
        kp2, desc2 = self.detect_and_describe(img2)
        
        matches = self.match_keypoints(desc1, desc2)
        
        H, mask = self.find_homography(kp1, kp2, matches)
        
        if H is None:
            raise ValueError("Không thể tính Homography. Kiểm tra lại ảnh đầu vào.")
        
        panorama = self.warp_images(img1, img2, H)
        
        info = {
            'keypoints1': len(kp1),
            'keypoints2': len(kp2),
            'matches': len(matches),
            'inliers': int(np.sum(mask)) if mask is not None else 0,
            'homography': H
        }
        
        if show_matches:
            matches_img = cv2.drawMatches(img1, kp1, img2, kp2, matches, None,
                                         flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
            info['matches_image'] = matches_img
            
        return panorama, info
    
    def stitch_multiple(self, images: List[np.ndarray]) -> Tuple[np.ndarray, List[dict]]:
        """
        Ghép nhiều ảnh thành panorama
        """
        if len(images) < 2:
            raise ValueError("Cần ít nhất 2 ảnh để ghép panorama")
        
        panorama = images[0]
        infos = []
        
        for i in range(1, len(images)):
            print(f"Đang ghép ảnh {i+1}/{len(images)}...")
            pano_temp, info = self.stitch_pair(panorama, images[i])
            panorama = pano_temp
            infos.append(info)
            
        return panorama, infos


def draw_keypoints(image: np.ndarray, keypoints: List) -> np.ndarray:
    """
    Vẽ keypoints lên ảnh
    """
    image_with_kp = cv2.drawKeypoints(image, keypoints, None, 
                                      flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    return image_with_kp