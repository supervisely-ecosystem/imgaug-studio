import imgaug.augmenters as iaa


def build_pipeline(names, params, random_order=False):
    pipeline = []
    for name, params_dict in zip(names, params):
        aug_f = getattr(iaa, name)
        pipeline.append(aug_f(**params_dict))
    augs = iaa.Sequential(pipeline, random_order=random_order)
    return augs


def build(name, param_dict):
    return build_pipeline([name], [param_dict])


def apply(img, augs: iaa.Sequential):
    res = augs(images=[img])
    return res[0]


# pipeline = [
#     iaa.imgcorruptlike.GaussianBlur(severity=(1, 5)),
#     iaa.Fliplr(p=1),
#     iaa.Sometimes(0.8, iaa.PadToFixedSize(width=1000, height=1000))
# ]
# augs = iaa.Sequential(pipeline, random_order=False)
# img_rgb = sly.image.read("cat.jpg")
# res = augs(images=[img_rgb])
# sly.image.write("res.jpg", res[0])