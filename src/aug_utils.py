import imgaug.augmenters as iaa
from copy import copy


def build_pipeline(names, params, random_order=False):
    pipeline = []
    for name, params_dict in zip(names, params):
        arguments = copy(params_dict)
        sometimes = arguments.pop("sometimes")
        sometimes_p = arguments.pop("sometimesP")
        aug_f = getattr(iaa, name) #@TODO: module.method
        if sometimes is False:
            pipeline.append(aug_f(**arguments))
        else:
            pipeline.append(iaa.meta.Sometimes(sometimes_p, aug_f(**arguments)))
    augs = iaa.Sequential(pipeline, random_order=random_order)
    return augs


def build(name, param_dict):
    return build_pipeline([name], [param_dict])


def apply(img, augs: iaa.Sequential):
    res = augs(images=[img])
    return res[0]


def generate_python_pypeline(names, params, random_order=False):
    template = """
    import imgaug.augmenters as iaa
    
    pipeline = [
        {}
    ]
    """


def generate_python(category_name, aug_name, default_params, params):
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
    if "sometimesP" in params:
        p = params["sometimesP"]
        if p < 1 and type(p) in [float]:
            res = f"iaa.Sometimes({p}, {method_py_final})"
    return res
