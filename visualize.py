from typing import List
import cv2
import numpy as np
import matplotlib.pyplot as plt


def heatmap(data, ax=None, cbar_kw=None, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (M, N).
    row_labels
        A list or array of length M with the labels for the rows.
    col_labels
        A list or array of length N with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current Axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.

    Usage:
      >>> fig, ax = plt.subplots()
      >>> im, cbar = heatmap(img, ax=ax, cmap="YlGn", cbarlabel="diff")
      >>> fig.tight_layout()
      >>> plt.show()
    """

    if ax is None:
        ax = plt.gca()

    if cbar_kw is None:
        cbar_kw = {}

    # Plot the heatmap
    im = ax.imshow(data, interpolation="nearest", **kwargs)
    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")
    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)

    return im, cbar


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


class ColorBar(object):
    """
    Get multiple colors

    Usage:
      >>> rgb_bar = ColorBar(mode="rgb)
      >>> bar = rgb_bar.bar
      >>> assert black in rgb_bar.namedcolors
      >>> black = rgb_bar.BLACK
    """

    __COLOR_BGR = {
        "black": (0, 0, 0),
        "blue": (255, 0, 0),
        "cyan": (255, 255, 0),
        "green": (0, 255, 0),
        "magenta": (255, 0, 255),
        "purple": (128, 0, 128),
        "red": (0, 0, 255),
        "white": (255, 255, 255),
        "yellow": (0, 255, 255),
    }

    def __init__(self, mode="bgr", black_in_bar=False):
        assert mode in ("bgr", "rgb")
        self.mode = mode
        self.__bar = create_color_bar(black_in_bar)

        for k, v in self.__COLOR_BGR.items():
            v = v[::-1] if self.mode == "rgb" else v
            self.__setattr__(k.upper(), v)

    @property
    def bar(self) -> np.ndarray:
        return self.__bar

    @property
    def namedcolors(self) -> List[str]:
        return list(self.__COLOR_BGR.keys())
