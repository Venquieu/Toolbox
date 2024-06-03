import os
import xmltodict
from typing import List, Dict


class AnnotationInstance(object):
    EMPTY = ""

    def __init__(self, info: dict) -> None:
        self.__info = info
        self.__points = None
        self.__iscrowd = None

    def merge(self, ann_b):
        assert (
            self.label_name == ann_b.label_name
        ), "Expect annotations with same label for merge! Got %s and %s " % (
            self.label_name,
            ann_b.label_name,
        )

        self.__points = self.points + ann_b.points
        self.__iscrowd = self.iscrowd or ann_b.iscrowd

    @property
    def points(self) -> List[list]:
        if self.__points:
            return self.__points

        self.__points = [[]]  # In case is a truncated object
        point_string_list = self.__info["@points"].split(";")
        for point_string in point_string_list:
            point = [float(x) for x in point_string.split(",")]
            self.__points[0].append(point)
        return self.__points

    @property
    def label_name(self) -> str:
        return self.__info["@label"]

    @property
    def group_id(self) -> str:
        if "@group_id" not in self.__info:
            return self.EMPTY
        return self.__info["@group_id"]

    @property
    def iscrowd(self) -> bool:
        if self.__iscrowd:
            return self.__iscrowd

        self.__parse_attri()
        self.__iscrowd = self.__iscrowd or False
        return self.__iscrowd

    @property
    def has_category(self) -> bool:
        return self.category != self.EMPTY


class ImageInstance(object):
    def __init__(self, info: dict) -> None:
        self.__info = info
        self.__ann = None

    @property
    def frame_id(self) -> int:
        return int(self.__info["@id"])

    @property
    def name(self) -> str:
        return self.__info["@name"]

    @property
    def basename(self) -> str:
        return os.path.basename(self.name)

    @property
    def height(self) -> int:
        return int(self.__info["@height"])

    @property
    def width(self) -> int:
        return int(self.__info["@width"])

    @property
    def annotations(self) -> List[AnnotationInstance]:
        if self.__ann:
            return self.__ann

        self.__ann = []
        if "polygon" not in self.__info:
            return self.__ann

        polygons = self.__info["polygon"]
        polygons = polygons if isinstance(polygons, list) else [polygons]
        recorder = {}  # k: group_id, v: idx
        for polygon in polygons:
            ann = AnnotationInstance(polygon)
            if ann.group_id == ann.EMPTY:
                self.__ann.append(ann)
                continue
            # has group
            if ann.group_id not in recorder:
                recorder[ann.group_id] = len(self.__ann)
                self.__ann.append(ann)
                continue
            # same group in list
            try:
                self.__ann[recorder[ann.group_id]].merge(ann)
            except AssertionError as e:
                print("Frame_id: %d, basename: %s" % (self.frame_id, self.basename))
                raise e

        return self.__ann

    @property
    def has_annotated(self) -> bool:
        return len(self.annotations) > 0


class ProjectInstance(object):
    def __init__(self, file) -> None:
        self.name = os.path.splitext(os.path.basename(file))[0]

        with open(file, mode="r", encoding="utf-8") as f:
            self.__info = xmltodict.parse(f.read())

        job_info = self.meta["task"]["segments"]["segment"]
        job_info = job_info if isinstance(job_info, list) else [job_info]
        self.__segments = {}
        for job in job_info:
            job_id = int(job["url"].split("=")[-1])
            self.__segments[job_id] = (int(job["start"]), int(job["stop"]))

        self.__images = None
        self.__url = None

    def frame2job(self, frame_id: int) -> int:
        for job_id, ranges in self.__segments.items():
            if ranges[0] <= frame_id <= ranges[1]:
                return job_id
        raise ValueError(f"invalid frame id: {frame_id}")

    def create_url(
        self, job_id: int = None, frame_id: int = None, basename: str = None
    ) -> str:
        if basename is not None:
            frame_id = self.images[basename].frame_id
        if frame_id is not None:
            job_id = self.frame2job(frame_id)
            return f"{self.url}/jobs/{job_id}?frame={frame_id}"
        if job_id is not None:
            return f"{self.url}/jobs/{job_id}"
        return self.url

    @property
    def task_id(self) -> int:
        return int(self.meta["task"]["id"])

    @property
    def meta(self) -> dict:
        return self.__info["annotations"]["meta"]

    @property
    def url(self) -> str:
        if self.__url:
            return self.__url
        self.__url = self.__segments[0]["url"].split("?")[0].strip(":8080/")
        return self.__url

    @property
    def images(self) -> Dict[str, ImageInstance]:
        if self.__images:
            return self.__images

        self.__images = {}
        img_list = self.__info["annotations"]["image"]
        img_list = img_list if isinstance(img_list, list) else [img_list]
        for img_info in img_list:
            img_ins = ImageInstance(img_info)
            try:
                _ = img_ins.annotations
            except AssertionError as e:
                url = self.create_url(frame_id=img_ins.frame_id)
                print("CVAT link: %s" % url)
                raise e

            self.__images[img_ins.basename] = img_ins
        return self.__images
