from typing import Union

import cv2
import numpy as np


def sigmoid(x: np.ndarray):
    return 1 / (1 + np.exp(-x))


def sigmoid_remap(x: np.ndarray, mean: Union[int, float], radius: Union[int, float]):
    return 2 * (sigmoid(x - mean) - 0.5) * radius + mean


class White2Colour(object):
    def __init__(self, hue_mean: int, hue_range: int = 5):
        self.hue_mean = hue_mean
        self.hue_range = hue_range

    def __call__(self, img, mask=None):
        """
        Args:
            img(np.ndarray): image in BGR colorspace
            mask(np.ndarray): bool mask
        """
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        new_hue = sigmoid_remap(hsv[..., 0], self.hue_mean, self.hue_range).astype(
            np.uint8
        )
        new_sut = (6 * hsv[..., 1]).clip(180, 230)

        if mask:
            hsv[..., 0] = np.logical_not(mask) * hsv[..., 0] + mask * new_hue
            hsv[..., 1] = np.logical_not(mask) * hsv[..., 1] + mask * new_sut
        else:
            hsv[..., 0] = new_hue
            hsv[..., 1] = new_sut

        img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        return img
