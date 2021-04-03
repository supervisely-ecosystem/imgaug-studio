import os
import supervisely_lib as sly
import imgaug.augmenters as iaa

import init_ui as ui
from init_ui import augs_configs
from cache import get_random_image
import aug_utils

app: sly.AppService = sly.AppService()

team_id = int(os.environ['context.teamId'])
workspace_id = int(os.environ['context.workspaceId'])
project_id = int(os.environ['modal.state.slyProjectId'])

project_info = app.public_api.project.get_info_by_id(project_id)
if project_info is None:
    raise RuntimeError(f"Project id={project_id} not found")

meta = sly.ProjectMeta.from_json(app.public_api.project.get_meta(project_id))
pipeline = []


@app.callback("preview")
@sly.timeit
def preview(api: sly.Api, task_id, context, state, app_logger):
    category_name = state["category"]
    aug_name = state["aug"]

    aug_info = augs_configs[category_name][aug_name]
    default_params = augs_configs[category_name][aug_name]["params"]

    final_params = {}
    for param_info in default_params:
        param_value = state["augVModels"][category_name][aug_name][param_info["pname"]]
        if type(param_value) is list:
            param_value = tuple(param_value)
        final_params[param_info["pname"]] = param_value

    img_info, img = get_random_image(api)

    aug = aug_utils.build(aug_name, final_params)
    res_img = aug_utils.apply(img, aug)

    # fields = [
    #     {"field": "data.progressPreview", "payload": "123"},
    #     {"field": "data.progressPreviewTotal", "payload": 23},
    # ]
    # api.task.set_fields(task_id, fields)
    # pass


def do(x, y=7):
    print("x + y = ", x + y)


def main():

    name = "do"
    params = {
        "x": 1,
        "y": 2
    }
    method = globals()[name]
    #method = locals()[name]
    method(**params)

    data = {}
    state = {}

    cache_images(app.public_api, project_id)
    ui.init_input_project(app.public_api, data, project_info)
    ui.init_pipeline(data, state)
    ui.init_augs_configs(data, state)

    app.run(data=data, state=state)

# @TODO: random_order flag
# https://stackoverflow.com/questions/3061/calling-a-function-of-a-module-by-using-its-name-a-string
# Cutout invalid arguments
# create sequence format
# add doc html
# refresh preview python code + images
# define minimum version
# add probability to every augmentation
# add shuffle flag to entire pipeline
# auto modify py field
# https://github.com/IliaLarchenko/albumentations-demo
if __name__ == "__main__":
    sly.main_wrapper("main", main)

