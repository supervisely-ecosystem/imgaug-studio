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


def generate_python(name, default_params, params):
    pstr = ""
    for item in default_params:
        name = item["pname"]
        value = params[name]
        if type(value) is str:
            pstr += f"{name}='{value}', "
        else:
            pstr += f"{name}={value}, "
    method_py_final = f"iaa.{name}({pstr[:-2]})"
    return method_py_final


# name = "do"
# params = {
#     "x": 1,
#     "y": 2
# }
# method = globals()[name]
# #method = locals()[name]
# method(**params)