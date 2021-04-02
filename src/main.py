import os
import numpy as np
import inspect
import supervisely_lib as sly
import json
#from docstring_parser import parse as doc_parse


#from mmseg.datasets.pipelines import Compose
from mmcls.datasets.pipelines import Compose
def mmcv_example():
    img_norm_cfg = dict(
        mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)

    pipeline = [
        dict(type='LoadImageFromFile'),
        dict(type='RandomResizedCrop', size=224),
        dict(type='RandomFlip', flip_prob=0.5, direction='horizontal'),
        dict(type='Normalize', **img_norm_cfg),
        dict(type='ImageToTensor', keys=['img']),
        dict(type='ToTensor', keys=['gt_label']),
        dict(type='Collect', keys=['img', 'gt_label'])
    ]

    info = {
        'img_prefix': '',
        'img_info': {'filename': "cat.jpg"},
        'gt_label': np.array(777, dtype=np.int64)
    }
    augs = Compose(pipeline)
    res = augs(info)
    x = 10
    x += 1

import imgaug
import imgaug.augmenters as iaa
from imgaug.augmentables.segmaps import SegmentationMapsOnImage
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
    # sly.fs.silent_remove("res.jpg")
    # imgaug_example()

    # # iaa.Fliplr
    #func_doc = iaa.Rotate.__doc__
    #print(func_doc)

    from augs import augs_modules

    for module_name, methods in augs_modules.items():
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

            # dp = doc_parse(method.__doc__)
            # param_desc = {item.arg_name: item.description.replace('\n', '.').replace('\r', '') for item in dp.params}
            # for param in method_info.parameters.values():
            #     print(f"\t\t {param.name} - {param_desc[param.name]}")




# https://albumentations-demo.herokuapp.com/
# https://towardsdatascience.com/explore-image-augmentations-using-a-convenient-tool-a199b4ac8214
# https://github.com/IliaLarchenko/albumentations-demo
# https://stackoverflow.com/questions/22212470/parsing-function-docstring-in-sphinx-autodoc-format
# формат параметров
if __name__ == "__main__":
    main()

