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

