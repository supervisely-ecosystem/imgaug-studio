import imgaug.augmenters as iaa
import inspect
import supervisely_lib as sly


def get_function(category_name, aug_name):
    try:
        submodule = getattr(iaa, category_name)
        aug_f = getattr(submodule, aug_name)
        return aug_f
    except Exception as e:
        sly.logger.error(repr(e))
        #raise e
        return None


# def get_defaults_by_function(f):
#     params = []
#     method_info = inspect.signature(f)
#     for param in method_info.parameters.values():
#         formatted = str(param)
#         if 'deprecated' in formatted or 'seed=None' in formatted or 'name=None' in formatted:
#             continue
#         if param.default == inspect._empty:
#             continue
#         params.append({
#             "pname": param.name,
#             "default": param.default
#         })
#     return params
#
#
# def get_default_by_name(category_name, aug_name):
#     func = get_function(category_name, aug_name)
#     defaults = get_defaults_by_function(func)
#     return defaults




