import imgaug.augmenters as iaa
import inspect
from collections import OrderedDict
import supervisely_lib as sly
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
from imgaug.augmentables.segmaps import SegmentationMapsOnImage
import numpy as np


def get_function(category_name, aug_name):
    try:
        submodule = getattr(iaa, category_name)
        aug_f = getattr(submodule, aug_name)
        return aug_f
    except Exception as e:
        sly.logger.error(repr(e))
        # raise e
        return None


def build_pipeline(aug_infos, random_order=False):
    pipeline = []
    for aug_info in aug_infos:
        category_name = aug_info["category"]
        aug_name = aug_info["name"]
        params = aug_info["params"]

        aug_func = get_function(category_name, aug_name)
        aug = aug_func(**params)

        sometimes = aug_info.get("sometimes", None)
        if sometimes is not None:
            aug = iaa.meta.Sometimes(sometimes, aug)
        pipeline.append(aug)
    augs = iaa.Sequential(pipeline, random_order=random_order)
    return augs


def build(aug_info):
    return build_pipeline([aug_info])


def create_aug_info(category_name, aug_name, params, sometimes: float = None):
    clean_params = remove_unexpected_arguments(category_name, aug_name, params)
    res = {
        "category": category_name,
        "name": aug_name,
        "params": clean_params,
    }
    if sometimes is not None:
        if type(sometimes) is not float or not (0.0 <= sometimes <= 1.0):
            raise ValueError(f"sometimes={sometimes}, type != {type(sometimes)}")
        res["sometimes"] = sometimes
    res["python"] = aug_to_python(res)
    return res


def apply(augs: iaa.Sequential, img, ann):
    bbs, segmaps = to_imgaug_annotations(ann)
    res = augs(images=[img], bounding_boxes=bbs, segmentation_maps=segmaps)
    return res[0]


def get_default_params_by_function(f):
    params = []
    method_info = inspect.signature(f)
    for param in method_info.parameters.values():
        formatted = str(param)
        if 'deprecated' in formatted or 'seed=None' in formatted or 'name=None' in formatted:
            continue
        if param.default == inspect._empty:
            continue
        params.append({
            "pname": param.name,
            "default": param.default
        })
    return params


def get_default_params_by_name(category_name, aug_name):
    func = get_function(category_name, aug_name)
    defaults = get_default_params_by_function(func)
    return defaults


def remove_unexpected_arguments(category_name, aug_name, params):
    # to avoid this:
    # TypeError: f() got an unexpected keyword argument 'b'
    defaults = get_default_params_by_name(category_name, aug_name)
    allowed_names = [d["pname"] for d in defaults]

    res = OrderedDict()
    for name, value in params.items():
        if name in allowed_names:
            res[name] = value
    return res


def aug_to_python(aug_info):
    pstr = ""
    for name, value in aug_info["params"].items():
        if type(value) is str:
            pstr += f"{name}='{value}', "
        else:
            pstr += f"{name}={value}, "
    method_py = f"iaa.{aug_info['category']}.{aug_info['name']}({pstr[:-2]})"

    res = method_py
    if "sometimes" in aug_info:
        res = f"iaa.Sometimes({aug_info['sometimes']}, {method_py})"
    return res


def pipeline_to_python(aug_infos, random_order=False):
    template = \
        """import imgaug.augmenters as iaa
        
        seq = iaa.Sequential([
        {}
        ], random_order={})
        """
    py_lines = [info["python"] for info in aug_infos]
    res = template.format('\t' + ',\n\t'.join(py_lines), random_order)
    return res


def boxes_from_sly_to_imgaug(ann: sly.Annotation) -> BoundingBoxesOnImage:
    boxes = []
    for label in ann.labels:
        if type(label.geometry) == sly.Rectangle:
            rect: sly.Rectangle = label.geometry
            boxes.append(
                BoundingBox(x1=rect.left, y1=rect.top, x2=rect.right, y2=rect.bottom, label=label.obj_class.name))
    bbs = None
    if len(boxes) > 0:
        bbs = BoundingBoxesOnImage(boxes, shape=ann.img_size)
    return bbs


def masks_from_sly_to_imgaug(ann: sly.Annotation) -> SegmentationMapsOnImage:
    masks = []
    for label in ann.labels:
        if type(label.geometry) == sly.Bitmap:
            bbox: sly.Rectangle = label.geometry.to_bbox()
            temp_label = label.translate(drow=-bbox.top, dcol=-bbox.left)
            mask = np.zeros((bbox.height, bbox.width, 1), dtype=bool)
            temp_label.draw(mask, [True])
            masks.append(mask)
    segmaps = None
    if len(masks) > 0:
        segmaps = SegmentationMapsOnImage([masks], shape=ann.img_size)
    return segmaps
