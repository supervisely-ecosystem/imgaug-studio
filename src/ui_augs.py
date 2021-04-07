from ui import augs_configs


def ui_to_params(state, category_name, aug_name):
    ui_defaults = augs_configs[category_name][aug_name]["params"]
    ui_vmodels = state["augVModels"][category_name][aug_name]
    params = _normalize_params(ui_defaults, ui_vmodels)
    _try_add_sometime(state, params)
    return params


def _normalize_params(default_params: dict, params: dict):
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


def _try_add_sometime(state, params):
    sometimes_p = state["sometimesP"] if state["sometimes"] else None
    if state["sometimes"]:
        params["sometimes"] = state["sometimesP"]
