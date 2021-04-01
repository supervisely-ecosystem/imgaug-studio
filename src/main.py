import os
from mmseg.datasets.pipelines import Compose


def main():
    img_norm_cfg = dict(
        mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)

    train_pipeline = [
        dict(type='LoadImageFromFile'),
        dict(type='RandomResizedCrop', size=224),
        dict(type='RandomFlip', flip_prob=0.5, direction='horizontal'),
        dict(type='Normalize', **img_norm_cfg),
        dict(type='ImageToTensor', keys=['img']),
        dict(type='ToTensor', keys=['gt_label']),
        dict(type='Collect', keys=['img', 'gt_label'])
    ]

    augs = Compose(pipeline)

    x = 10
    x += 1


if __name__ == "__main__":
    main()
