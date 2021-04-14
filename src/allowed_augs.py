import imgaug.augmenters.arithmetic as arithmetic
import imgaug.augmenters.artistic as artistic
import imgaug.augmenters.blend as blend
import imgaug.augmenters.blur as blur
import imgaug.augmenters.collections as iaa_collections
import imgaug.augmenters.color as color
import imgaug.augmenters.contrast as contrast
import imgaug.augmenters.convolutional as convolutional
import imgaug.augmenters.edges as edges
import imgaug.augmenters.flip as flip
import imgaug.augmenters.geometric as geometric
import imgaug.augmenters.imgcorruptlike as imgcorruptlike
import imgaug.augmenters.meta as meta
import imgaug.augmenters.pillike as pillike
import imgaug.augmenters.pooling as pooling
import imgaug.augmenters.segmentation as segmentation
import imgaug.augmenters.size as size
import imgaug.augmenters.weather as weather


augs_modules = {
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
        # arithmetic.TotalDropout,
        # arithmetic.ReplaceElementwise,
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
    # "artistic": [
    #     artistic.Cartoon
    # ],
    # "blend": [
    #     blend.BlendAlpha,
    #     blend.BlendAlphaMask,
    #     blend.BlendAlphaElementwise,
    #     blend.BlendAlphaSimplexNoise,
    #     blend.BlendAlphaFrequencyNoise,
    #     blend.BlendAlphaSomeColors,
    #     blend.BlendAlphaHorizontalLinearGradient,
    #     blend.BlendAlphaVerticalLinearGradient,
    #     blend.BlendAlphaSegMapClassIds,
    #     blend.BlendAlphaBoundingBoxes,
    #     blend.BlendAlphaRegularGrid,
    #     blend.BlendAlphaCheckerboard,
    # ],
    "blur": [
        blur.GaussianBlur,
        blur.AverageBlur,
        blur.MedianBlur,
        blur.BilateralBlur,
        blur.MotionBlur,
        blur.MeanShiftBlur,
    ],
    # "collections": [
    #     iaa_collections.RandAugment,
    # ],
    "color": [
        # color.WithColorspace,
        # color.WithBrightnessChannels,
        color.MultiplyAndAddToBrightness,
        color.MultiplyBrightness,
        color.AddToBrightness,
        # color.WithHueAndSaturation,
        color.MultiplyHueAndSaturation,
        color.MultiplyHue,
        color.MultiplySaturation,
        color.RemoveSaturation,
        color.AddToHueAndSaturation,
        color.AddToHue,
        color.AddToSaturation,
        # color.ChangeColorspace,
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
        #convolutional.Convolve,
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
        #geometric.Affine,
        geometric.ScaleX,
        geometric.ScaleY,
        geometric.TranslateX,
        geometric.TranslateY,
        geometric.Rotate,
        geometric.ShearX,
        geometric.ShearY,
        geometric.AffineCv2,
        geometric.PiecewiseAffine,
        geometric.PerspectiveTransform,
        geometric.ElasticTransformation,
        geometric.Rot90,
        geometric.WithPolarWarping,
        geometric.Jigsaw,
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
        imgcorruptlike.ElasticTransform,
    ],
    # "meta": [
    #     meta.Sequential,
    #     meta.SomeOf,
    #     meta.OneOf,
    #     meta.Sometimes,
    #     meta.WithChannels,
    #     meta.Identity,
    #     meta.Noop,
    #     # meta.Lambda,
    #     # meta.AssertLambda,
    #     # meta.AssertShape,
    #     meta.ChannelShuffle,
    # ],
    "pillike": [
        pillike.Solarize,
        pillike.Posterize,
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
        pillike.Affine,
    ],
    "pooling": [
        pooling.AveragePooling,
        pooling.MaxPooling,
        pooling.MinPooling,
        pooling.MedianPooling,
    ],
    "segmentation": [
        segmentation.Superpixels,
        segmentation.Voronoi,
        segmentation.UniformVoronoi,
        segmentation.RegularGridVoronoi,
        segmentation.RelativeRegularGridVoronoi,
    ],
    "size": [
        size.Resize,
        size.CropAndPad,
        size.Crop,
        size.Pad,
        size.PadToFixedSize,
        size.CenterPadToFixedSize,
        size.CropToFixedSize,
        size.CenterCropToFixedSize,
        size.CropToMultiplesOf,
        size.CenterCropToMultiplesOf,
        size.PadToMultiplesOf,
        size.CenterPadToMultiplesOf,
        size.CropToPowersOf,
        size.CenterCropToPowersOf,
        size.PadToPowersOf,
        size.CenterPadToPowersOf,
        size.CropToAspectRatio,
        size.CenterCropToAspectRatio,
        size.PadToAspectRatio,
        size.CenterPadToAspectRatio,
        size.CropToSquare,
        size.CenterCropToSquare,
        size.PadToSquare,
        size.CenterPadToSquare,
        size.KeepSizeByResize,
    ],
    "weather": [
        weather.FastSnowyLandscape,
        weather.CloudLayer,
        weather.Clouds,
        weather.Fog,
        weather.SnowflakesLayer,
        weather.Snowflakes,
        weather.RainLayer,
        weather.Rain,
    ]
}
