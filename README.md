<div align="center" markdown>
<img src="https://user-images.githubusercontent.com/48245050/182815780-667460f6-b056-4e18-9d06-da5b7de01175.png"/>

# ImgAug Studio

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Use">How To Use</a>
</p>


[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/imgaug-studio)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/imgaug-studio)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/imgaug-studio)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/imgaug-studio)](https://supervise.ly)

</div>

# Overview

ImgAug Studio is a wrapper around great [ImgAug Library](https://github.com/aleju/imgaug). Interactive UI helps to 
understand how image transformations work and illustrates how to use this library with Supervisely Format. 

Once augmentations are combined into pipeline, they can be exported to both `python` file (for developers) and safer 
serialization format `json`. This `json` config can be used for real-time augmentations during training for some 
Neural Networks from Supervisely Ecosystem.  

Only labels of types `Polygon`, `Rectangle` and `Bitmap` in supervisely format can be converted automatically to imgaug 
format (and vice versa). 

# List of supported augmentations

```python
{
    "arithmetic": [
        arithmetic.Add,
        arithmetic.AddElementwise,
        arithmetic.AdditiveGaussianNoise,
        arithmetic.AdditiveLaplaceNoise,
        arithmetic.AdditivePoissonNoise,
        arithmetic.Multiply,
        arithmetic.MultiplyElementwise,
        arithmetic.Cutout,
        arithmetic.Dropout,
        arithmetic.CoarseDropout,
        arithmetic.Dropout2d,
        arithmetic.ImpulseNoise,
        arithmetic.SaltAndPepper,
        arithmetic.CoarseSaltAndPepper,
        arithmetic.Salt,
        arithmetic.CoarseSalt,
        arithmetic.Pepper,
        arithmetic.CoarsePepper,
        arithmetic.Invert,
        arithmetic.Solarize,
        arithmetic.ContrastNormalization,
        arithmetic.JpegCompression,
    ],
    "blur": [
        blur.GaussianBlur,
        blur.AverageBlur,
        blur.MedianBlur,
        blur.BilateralBlur,
        blur.MotionBlur,
        blur.MeanShiftBlur,
    ],
    "color": [
        color.MultiplyAndAddToBrightness,
        color.MultiplyBrightness,
        color.AddToBrightness,
        color.MultiplyHueAndSaturation,
        color.MultiplyHue,
        color.MultiplySaturation,
        color.RemoveSaturation,
        color.AddToHueAndSaturation,
        color.AddToHue,
        color.AddToSaturation,
        color.Grayscale,
        color.ChangeColorTemperature,
        color.KMeansColorQuantization,
        color.UniformColorQuantization,
        color.Posterize,
    ],
    "contrast": [
        contrast.GammaContrast,
        contrast.SigmoidContrast,
        contrast.LogContrast,
        contrast.LinearContrast,
        contrast.AllChannelsHistogramEqualization,
        contrast.HistogramEqualization,
        contrast.AllChannelsCLAHE,
        contrast.CLAHE,
    ],
    "convolutional": [
        convolutional.Sharpen,
        convolutional.Emboss,
        convolutional.EdgeDetect,
        convolutional.DirectedEdgeDetect,
    ],
    "flip": [
        flip.Fliplr,
        flip.Flipud,
    ],
    "geometric": [
        geometric.ScaleX,
        geometric.ScaleY,
        geometric.TranslateX,
        geometric.TranslateY,
        geometric.Rotate,
        geometric.ShearX,
        geometric.ShearY,
        geometric.PiecewiseAffine,
        geometric.PerspectiveTransform,
        geometric.ElasticTransformation,
        geometric.Rot90,
    ],
    "imgcorruptlike": [
        imgcorruptlike.GaussianNoise,
        imgcorruptlike.ShotNoise,
        imgcorruptlike.ImpulseNoise,
        imgcorruptlike.SpeckleNoise,
        imgcorruptlike.GaussianBlur,
        imgcorruptlike.GlassBlur,
        imgcorruptlike.DefocusBlur,
        imgcorruptlike.MotionBlur,
        imgcorruptlike.ZoomBlur,
        imgcorruptlike.Fog,
        imgcorruptlike.Frost,
        imgcorruptlike.Snow,
        imgcorruptlike.Spatter,
        imgcorruptlike.Contrast,
        imgcorruptlike.Brightness,
        imgcorruptlike.Saturate,
        imgcorruptlike.JpegCompression,
        imgcorruptlike.Pixelate,
    ],
    "pillike": [
        pillike.Solarize,
        pillike.Equalize,
        pillike.Autocontrast,
        pillike.EnhanceColor,
        pillike.EnhanceContrast,
        pillike.EnhanceBrightness,
        pillike.EnhanceSharpness,
        pillike.FilterBlur,
        pillike.FilterSmooth,
        pillike.FilterSmoothMore,
        pillike.FilterEdgeEnhance,
        pillike.FilterEdgeEnhanceMore,
        pillike.FilterFindEdges,
        pillike.FilterContour,
        pillike.FilterEmboss,
        pillike.FilterSharpen,
        pillike.FilterDetail,
    ],
    "segmentation": [
        segmentation.Superpixels,
        segmentation.UniformVoronoi,
        segmentation.RegularGridVoronoi,
        segmentation.RelativeRegularGridVoronoi,
    ],
}
```

# How To Use

1. Add app to your team from Ecosystem
2. Run app from context menu of images project
3. Open app and start experiments
4. Close app manually


Watch short video for more details:

<a data-key="sly-embeded-video-link" href="https://youtu.be/zdjRMb8BlPU" data-video-code="zdjRMb8BlPU">
    <img src="https://i.imgur.com/ZQPmtfk.png" alt="SLY_EMBEDED_VIDEO_LINK"  style="max-width:100%;">
</a>

# For developers
Feature is available in `supervisely>=6.1.80`

```python
import supervisely_lib as sly
import json

# load json configuration of pipeline
filename = "/a/b/c/my_augs_pipeline.json"
# load augs pipeline from json
with open(filename, encoding='utf-8') as fin:
    config = json.load(fin)
# or
# config = sly.json.load_json_file(filename)

# ot imgaug ia.Sequential
augs = sly.imgaug_utils.build_pipeline(config["pipeline"], config["random_order"])


# prepare project meta (classes and tags), image and annotation
api = sly.Api.from_env()
project_id = 777
image_id = 123
meta = sly.ProjectMeta.from_json(api.project.get_meta(project_id))
img = api.image.download_np(image_id)
ann_json = api.annotation.download(image_id).annotation
ann = sly.Annotation.from_json(ann_json, meta)

# get augmentations in supervisely format 
# polygons will be converted to bitmaps, thus new classes will be created and stored in res_meta
res_meta, res_img, res_ann = sly.imgaug_utils.apply(augs, meta, img, ann)
```


# Screenshot

<img src="https://i.imgur.com/vQ9hrCI.png"/>
