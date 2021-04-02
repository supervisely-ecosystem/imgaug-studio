import os
import numpy as np
import inspect
import supervisely_lib as sly
import json
import imgaug
import imgaug.augmenters as iaa
from imgaug.augmentables.segmaps import SegmentationMapsOnImage
from augs import augs_modules


def imgaug_example():
    pipeline = [
        iaa.imgcorruptlike.GaussianBlur(severity=(1, 5)),
        iaa.Fliplr(p=1),
        iaa.Sometimes(0.8, iaa.PadToFixedSize(width=1000, height=1000))
    ]
    augs = iaa.Sequential(pipeline, random_order=False)
    img_rgb = sly.image.read("cat.jpg")
    res = augs(images=[img_rgb])
    sly.image.write("res.jpg", res[0])


def main():
    augs_config = {}
    for module_name, methods in augs_modules.items():
        augs_config[module_name] = {}
        print(module_name)
        for method in methods:
            method_info = inspect.signature(method)
            x = str(method_info)

            method_doc_url = f"https://imgaug.readthedocs.io/en/latest/source/api_augmenters_{module_name}.html#imgaug.augmenters.{module_name}.{method.__name__}"
            method_py = ""
            for param in method_info.parameters.values():
                formatted = str(param)
                if 'deprecated' in formatted or 'seed=None' in formatted or 'name=None' in formatted:
                    continue
                method_py += formatted + ", "
            print(method_doc_url)
            print(f"\t iaa.{method.__name__}({method_py[:-2]})")


# https://github.com/IliaLarchenko/albumentations-demo
if __name__ == "__main__":
    main()

