import json
import numpy as np


class Annotation(object):
    def __init__(self, ann_file: str) -> None:
        with open(ann_file, "r") as f:
            self.__content = json.load(f)

        self.__contours = None

    @property
    def image_path(self) -> str:
        return self.__content["imagePath"]

    @property
    def image_size(self) -> tuple:
        return (self.__content["imageHeight"], self.__content["imageWidth"])

    @property
    def label_names(self) -> list:
        return [label["label"] for label in self.__content["shapes"]]
    
    @property
    def contours(self) -> list:
        if self.__contours:
            return self.__contours

        self.__contours = []
        for item in self.__content["shapes"]:
            if item["shape_type"] != "polygon":
                continue
            contour = np.array(item["points"], dtype=np.int32)
            contour = np.reshape(contour, (-1, 2))
            self.__contours.append(contour)

        return self.__contours
