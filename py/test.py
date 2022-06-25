import numpy as np

img = np.zeros((480,640,3), dtype=np.int32)
sample_points_idx_1 = np.linspace(0,480-1,30,dtype=np.int32)
            
key_points = img[sample_points_idx_1,320,:]

print(key_points[0])