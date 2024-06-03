import cv2
import numpy as np


def create_color_bar(with_black=True) -> np.ndarray:
    H = (180, 90, 120, 60, 160, 10, 100, 40, 150, 30, 140, 80, 20)
    S = (250, 140, 160, 190, 220)
    V = (250, 180, 90, 210, 130)
    h_size, s_size, v_size = len(H), len(S), len(V)
    color_bar = np.zeros((1, h_size * s_size * v_size, 3))

    for i in range(h_size * s_size * v_size):
        color_bar[0][i] = np.array(
            [H[i % h_size], S[i % s_size], V[i % v_size]], dtype=np.uint8
        )
    color_bar = cv2.cvtColor(color_bar.astype(np.uint8), cv2.COLOR_HSV2BGR)
    if with_black:
        black = np.array([[0, 0, 0]], dtype=np.uint8)
        color_bar = np.concatenate([black, color_bar], axis=0)

    return np.squeeze(color_bar, axis=0)
