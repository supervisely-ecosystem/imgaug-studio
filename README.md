    """Apply affine rotation on the y-axis to input data.

    This is a wrapper around :class:`Affine`.
    It is the same as ``Affine(rotate=<value>)``.

    Added in 0.4.0.

    **Supported dtypes**:

    See :class:`~imgaug.augmenters.geometric.Affine`.

    Parameters
    ----------
    rotate : number or tuple of number or list of number or imgaug.parameters.StochasticParameter, optional
        See :class:`Affine`.

    order : int or iterable of int or imgaug.ALL or imgaug.parameters.StochasticParameter, optional
        See :class:`Affine`.

    cval : number or tuple of number or list of number or imgaug.ALL or imgaug.parameters.StochasticParameter, optional
        See :class:`Affine`.

    mode : str or list of str or imgaug.ALL or imgaug.parameters.StochasticParameter, optional
        See :class:`Affine`.

    fit_output : bool, optional
        See :class:`Affine`.

    backend : str, optional
        See :class:`Affine`.

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
    >>> aug = iaa.Rotate((-45, 45))

    Create an augmenter that rotates images by a random value between ``-45``
    and ``45`` degress.

    """
