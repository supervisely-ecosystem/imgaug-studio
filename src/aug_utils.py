import imgaug.augmenters as iaa


def build_pipeline(names, params, probs=None, random_order=False):
    if probs is None:
        probs = [None] * len(names)

    pipeline = []
    for name, params_dict, p in zip(names, params, probs):
        aug_f = getattr(iaa, name)
        if p is None:
            pipeline.append(aug_f(**params_dict))
        else:
            pipeline.append(iaa.meta.Sometimes(p, aug_f(**params_dict)))
    augs = iaa.Sequential(pipeline, random_order=random_order)
    return augs


def build(name, param_dict, sometimes_p=None):
    if sometimes_p is None:
        return build_pipeline([name], [param_dict])
    return build_pipeline([name], [param_dict], [sometimes_p])


def apply(img, augs: iaa.Sequential):
    res = augs(images=[img])
    return res[0]


def normalize_params(default_params: dict, params: dict):
    ptypes = {p["pname"]: p for p in default_params}
    res = {}
    for name, value in params.items():
        if ptypes[name]["type"] == 'el-slider-range':
            res[name] = tuple(value)
        elif ptypes[name]["type"] == 'el-input-number':
            try:
                res[name] = float(value)
            except ValueError as e:
                res[name] = float(ptypes[name]["default"])
        elif ptypes[name]["type"] == 'el-input-range':
            try:
                res[name] = tuple([int(value[0]), int(value[1])])
            except ValueError as e:
                res[name] = tuple(ptypes[name]["default"])
        elif ptypes[name]["type"] == 'el-input-number-range':
            try:
                res[name] = [int(value[0]), int(value[1])]
                res[name].sort()
                res[name] = tuple(res[name])
            except ValueError as e:
                res[name] = tuple(ptypes[name]["default"])
        else:
            res[name] = value
    return res


def generate_python_pypeline(names, params, random_order=False):
    template = """
    import imgaug.augmenters as iaa
    
    pipeline = [
        {}
    ]
    """


def generate_python(category_name, aug_name, default_params, params, sometimes_p=None):
    pstr = ""
    for item in default_params:
        name = item["pname"]
        value = params[name]
        if type(value) is str:
            pstr += f"{name}='{value}', "
        else:
            pstr += f"{name}={value}, "
    method_py_final = f"iaa.{category_name}.{aug_name}({pstr[:-2]})"
    res = method_py_final
    if sometimes_p is not None and sometimes_p < 1 and type(sometimes_p) in [float]:
        res = f"iaa.Sometimes({sometimes_p}, {method_py_final})"
    return res


# name = "do"
# params = {
#     "x": 1,
#     "y": 2
# }
# method = globals()[name]
# #method = locals()[name]
# method(**params)