import os
import numpy as np
import supervisely_lib as sly


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
    sly.fs.silent_remove("res.jpg")
    imgaug_example()


if __name__ == "__main__":
    main()
