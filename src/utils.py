import inspect
import supervisely_lib as sly
from allowed_augs import augs_modules


def get_param_type(default=None):
    if default is None:
        return {
            "type": "el-input-number",
            "default": 0,
            "min": 0,
            "max": 100
        }
    if type(default) is tuple:
        return {
            "type": "el-slider-range",
            "default": list(default),
            "min": 0,
            "max": 100
        }
    if type(default) is bool:
        return {
            "type": "el-checkbox",
            "default": default,
        }
    if isinstance(default, (int, float)):
        return {
            "type": "el-input-number",
            "default": default,
            "min": 0,
            "max": 100
        }
    if type(default) is str:
        return {
            "type": "el-select",
            "default": default,
            "options": [default]
        }
    if type(default) is list and type(default[0]) is str:
        return {
            "type": "el-select",
            "default": default,
            "options": default
        }
    if default == inspect._empty:
        return {}
    raise NotImplementedError("Unsupported value type")


def gen_auto_config():
    augs_config = {}
    for module_name, methods in augs_modules.items():
        module_augs = {}
        print(module_name)
        for method in methods:
            method_info = inspect.signature(method)
            method_doc_url = f"https://imgaug.readthedocs.io/en/latest/source/api_augmenters_{module_name}.html#imgaug.augmenters.{module_name}.{method.__name__}"
            method_py = ""
            params_config = []
            for param in method_info.parameters.values():
                formatted = str(param)
                if 'deprecated' in formatted or 'seed=None' in formatted or 'name=None' in formatted:
                    continue
                method_py += formatted + ", "
                param_info = get_param_type(param.default)
                if len(param_info) != 0:
                    param_info["pname"] = param.name
                    params_config.append(param_info)

            print(method_doc_url)
            method_py_final = f"iaa.{method.__name__}({method_py[:-2]})"
            print(method_py_final)

            module_augs[method.__name__] = {
                "durl": method_doc_url,
                "py": method_py_final,
                "params": params_config
            }

        augs_config[module_name] = module_augs

    sly.json.dump_json_file(augs_config, "augs_auto.json")