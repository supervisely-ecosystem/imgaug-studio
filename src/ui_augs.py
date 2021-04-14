from collections import OrderedDict
from ui import augs_configs
from imgaug_utils import create_aug_info


def get_aug_info(state):
    category_name = state["category"]
    aug_name = state["aug"]
    ui_defaults = augs_configs[category_name][aug_name]["params"]
    ui_vmodels = state["augVModels"][category_name][aug_name]
    sometimes = state["sometimesP"] if state["sometimes"] else None
    params = _normalize_params(ui_defaults, ui_vmodels)
    aug_info = create_aug_info(category_name, aug_name, params, sometimes)
    return aug_info


def _normalize_params(default_params: dict, params: dict):
    ptypes = {p["pname"]: p for p in default_params}
    res = OrderedDict()
    for name, value in params.items():
        if ptypes[name]["type"] == 'el-slider-range':
            res[name] = tuple(value)
        elif ptypes[name]["type"] == 'el-input-number' and ptypes[name].get('valueType') is not None:
            try:
                res[name] = int(value)
            except ValueError as e:
                res[name] = int(ptypes[name]["default"])
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


def _try_add_sometime(state, aug_info):
    if state["sometimes"]:
        aug_info["sometimes"] = state["sometimesP"]
