import imgaug.augmenters.arithmetic as arithmetic

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
        arithmetic.TotalDropout,
        arithmetic.ReplaceElementwise,
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
    ]
}
