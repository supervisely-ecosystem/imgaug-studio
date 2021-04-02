import os
import supervisely_lib as sly


def init_input_project(api: sly.Api, data: dict, project_info):
    data["projectId"] = project_info.id
    data["projectName"] = project_info.name
    data["projectPreviewUrl"] = api.image.preview_url(project_info.reference_image_url, 100, 100)
    data["projectItemsCount"] = project_info.items_count


def init_augs_configs(data: dict, state: dict):
    augs_configs = sly.json.load_json_file("augs.json")
    data["categories"] = list(augs_configs.keys())
    state["category"] = data["categories"][0]

    state["aug"] = None

    state["augVModels"] = {}

    augs_list = {}
    for category, augs in augs_configs.items():
        augs_list[category] = list(augs.keys())
        state["augVModels"][category] = {}
        for aug_name, info in augs.items():
            state["augVModels"][category][aug_name] = {}
            for param in info["params"]:
                state["augVModels"][category][aug_name][param["name"]] = param["default"]

    data["augs"] = augs_list
    data["config"] = augs_configs

    data["docstring"] = """
    Crop images down to a predefined maximum width and/or height.

    If images are already at the maximum width/height or are smaller, they
    will not be cropped. Note that this also means that images will not be
    padded if they are below the required width/height.

    The augmenter randomly decides per image how to distribute the required
    cropping amounts over the image axis. E.g. if 2px have to be cropped on
    the left or right to reach the required width, the augmenter will
    sometimes remove 2px from the left and 0px from the right, sometimes
    remove 2px from the right and 0px from the left and sometimes remove 1px
    from both sides. Set `position` to ``center`` to prevent that.

    **Supported dtypes**:

        * ``uint8``: yes; fully tested
        * ``uint16``: yes; tested
        * ``uint32``: yes; tested
        * ``uint64``: yes; tested
        * ``int8``: yes; tested
        * ``int16``: yes; tested
        * ``int32``: yes; tested
        * ``int64``: yes; tested
        * ``float16``: yes; tested
        * ``float32``: yes; tested
        * ``float64``: yes; tested
        * ``float128``: yes; tested
        * ``bool``: yes; tested

    Parameters
    ----------
    width : int or None
        Crop images down to this maximum width.
        If ``None``, image widths will not be altered.

    height : int or None
        Crop images down to this maximum height.
        If ``None``, image heights will not be altered.

    position : {'uniform', 'normal', 'center', 'left-top', 'left-center', 'left-bottom', 'center-top', 'center-center', 'center-bottom', 'right-top', 'right-center', 'right-bottom'} or tuple of float or StochasticParameter or tuple of StochasticParameter, optional
         Sets the center point of the cropping, which determines how the
         required cropping amounts are distributed to each side. For a
         ``tuple`` ``(a, b)``, both ``a`` and ``b`` are expected to be in
         range ``[0.0, 1.0]`` and describe the fraction of cropping applied
         to the left/right (low/high values for ``a``) and the fraction
         of cropping applied to the top/bottom (low/high values for ``b``).
         A cropping position at ``(0.5, 0.5)`` would be the center of the
         image and distribute the cropping equally over all sides. A cropping
         position at ``(1.0, 0.0)`` would be the right-top and would apply
         100% of the required cropping to the right and top sides of the image.

            * If string ``uniform`` then the share of cropping is randomly
              and uniformly distributed over each side.
              Equivalent to ``(Uniform(0.0, 1.0), Uniform(0.0, 1.0))``.
            * If string ``normal`` then the share of cropping is distributed
              based on a normal distribution, leading to a focus on the center
              of the images.
              Equivalent to
              ``(Clip(Normal(0.5, 0.45/2), 0, 1),
              Clip(Normal(0.5, 0.45/2), 0, 1))``.
            * If string ``center`` then center point of the cropping is
              identical to the image center.
              Equivalent to ``(0.5, 0.5)``.
            * If a string matching regex
              ``^(left|center|right)-(top|center|bottom)$``, e.g.
              ``left-top`` or ``center-bottom`` then sets the center point of
              the cropping to the X-Y position matching that description.
            * If a tuple of float, then expected to have exactly two entries
              between ``0.0`` and ``1.0``, which will always be used as the
              combination the position matching (x, y) form.
            * If a ``StochasticParameter``, then that parameter will be queried
              once per call to ``augment_*()`` to get ``Nx2`` center positions
              in ``(x, y)`` form (with ``N`` the number of images).
            * If a ``tuple`` of ``StochasticParameter``, then expected to have
              exactly two entries that will both be queried per call to
              ``augment_*()``, each for ``(N,)`` values, to get the center
              positions. First parameter is used for ``x`` coordinates,
              second for ``y`` coordinates.

    seed : None or int or imgaug.random.RNG or numpy.random.Generator or numpy.random.BitGenerator or numpy.random.SeedSequence or numpy.random.RandomState, optional
        See :func:`~imgaug.augmenters.meta.Augmenter.__init__`.

    name : None or str, optional
        See :func:`~imgaug.augmenters.meta.Augmenter.__init__`.

    random_state : None or int or imgaug.random.RNG or numpy.random.Generator or numpy.random.BitGenerator or numpy.random.SeedSequence or numpy.random.RandomState, optional
        Old name for parameter `seed`.
        Its usage will not yet cause a deprecation warning,
        but it is still recommended to use `seed` now.
        Outdated since 0.4.0.

    deterministic : bool, optional
        Deprecated since 0.4.0.
        See method ``to_deterministic()`` for an alternative and for
        details about what the "deterministic mode" actually does.

    Examples
    --------
    >>> import imgaug.augmenters as iaa
    >>> aug = iaa.CropToFixedSize(width=100, height=100)

    For image sides larger than ``100`` pixels, crop to ``100`` pixels. Do
    nothing for the other sides. The cropping amounts are randomly (and
    uniformly) distributed over the sides of the image.

    >>> aug = iaa.CropToFixedSize(width=100, height=100, position="center")

    For sides larger than ``100`` pixels, crop to ``100`` pixels. Do nothing
    for the other sides. The cropping amounts are always equally distributed
    over the left/right sides of the image (and analogously for top/bottom).

    >>> aug = iaa.Sequential([
    >>>     iaa.PadToFixedSize(width=100, height=100),
    >>>     iaa.CropToFixedSize(width=100, height=100)
    >>> ])

    Pad images smaller than ``100x100`` until they reach ``100x100``.
    Analogously, crop images larger than ``100x100`` until they reach
    ``100x100``. The output images therefore have a fixed size of ``100x100``.

    """

    state["py"] = ""