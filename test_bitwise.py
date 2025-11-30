import cv2
import numpy as np

# Create a black frame
frame = np.zeros((100, 100), dtype=np.uint8)
# Draw a white square in the middle (representing the eye content)
cv2.rectangle(frame, (30, 30), (70, 70), 128, -1)

# Create a mask: 0 inside eye, 255 outside
mask = np.full((100, 100), 255, dtype=np.uint8)
# Fill eye region with 0
cv2.rectangle(mask, (30, 30), (70, 70), 0, -1)

# Black frame for background
black_frame = np.zeros((100, 100), dtype=np.uint8)

# Apply bitwise_not
# We want: Outside (mask=255) -> White (255). Inside (mask=0) -> Original (128).
eye = cv2.bitwise_not(black_frame, frame.copy(), mask=mask)

# Check values
print(f"Outside pixel (0,0): {eye[0,0]}") # Should be 255
print(f"Inside pixel (50,50): {eye[50,50]}") # Should be 128
