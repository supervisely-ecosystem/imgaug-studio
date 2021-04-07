import os
import json
import supervisely_lib as sly

import ui
from cache import get_random_image, cache_images
import ui_augs
import imgaug_utils


app: sly.AppService = sly.AppService()

team_id = int(os.environ['context.teamId'])
workspace_id = int(os.environ['context.workspaceId'])
project_id = int(os.environ['modal.state.slyProjectId'])

project_info = app.public_api.project.get_info_by_id(project_id)
if project_info is None:
    raise RuntimeError(f"Project id={project_id} not found")

meta = sly.ProjectMeta.from_json(app.public_api.project.get_meta(project_id))
pipeline = []

vis_dir = os.path.join(app.data_dir, "vis_images")
sly.fs.mkdir(vis_dir)
sly.fs.clean_dir(vis_dir)  # convenient for debug


@app.callback("preview")
@sly.timeit
def preview(api: sly.Api, task_id, context, state, app_logger):
    category_name = state["category"]
    aug_name = state["aug"]

    params = ui_augs.ui_to_params(state, category_name, aug_name)



    # py_example = aug_utils.generate_python(category_name, aug_name, default_params, params)
    # aug = aug_utils.build(aug_name, params)
    #
    # preview_labels = []
    # preview_images = []
    # sync_keys = []
    #
    # img_info, img = get_random_image(api)
    # res_img = aug_utils.apply(img, aug)
    # preview_local_path = os.path.join(vis_dir, f"preview_image_{0}.png")
    # preview_remote_path = os.path.join(f"/imgaug-studio/{task_id}", f"preview_image_{0}.png")
    # sly.image.write(preview_local_path, res_img)
    #
    # if api.file.exists(team_id, preview_remote_path):
    #     api.file.remove(team_id, preview_remote_path)
    # file_info = api.file.upload(team_id, preview_local_path, preview_remote_path)
    #
    # sync_keys.append(["0", "1"])
    # preview_labels.extend([[], []])
    # preview_images.extend([img_info.full_storage_url, file_info.full_storage_url])
    #
    # CNT_GRID_COLUMNS, gallery = ui.get_empty_gallery()
    # grid_annotations = {}
    # grid_layout = [[] for i in range(CNT_GRID_COLUMNS)]
    # for idx, (image_url, labels) in enumerate(zip(preview_images, preview_labels)):
    #     grid_annotations[str(idx)] = {
    #         "url": image_url,
    #         "figures": labels
    #     }
    #     grid_layout[idx % CNT_GRID_COLUMNS].append(str(idx))
    # gallery["content"]["layout"] = grid_layout
    # gallery["content"]["annotations"] = grid_annotations
    # gallery["options"]["syncViewsBindings"] = sync_keys
    #
    # fields = [
    #     {"field": "data.gallery", "payload": gallery},
    #     {"field": "state.previewLoading", "payload": False},
    #     {"field": "data.previewPy", "payload": py_example},
    # ]
    # api.task.set_fields(task_id, fields)


@app.callback("add_to_pipeline")
@sly.timeit
def add_to_pipeline(api: sly.Api, task_id, context, state, app_logger):
    pass
    # category = state["category"]
    # aug = state["aug"]
    #
    # default_params =
    #
    #
    # augs_configs[category][aug]["params"]
    # params = aug_utils.normalize_params(default_params, state["augVModels"][category][aug])
    # if state["sometimes"]:
    #     params["sometimesP"] = state["sometimesP"]
    # py_example = aug_utils.generate_python(category, aug, default_params, params)
    #
    # aug_config = {
    #     "category": category,
    #     "aug": aug,
    #     "augVModels": params,  # optional in general
    #     "pyExample": py_example
    # }
    # print(json.dumps(aug_config, indent=4))
    # pipeline.append(aug_config)
    #
    # fields = [
    #     {"field": "data.pipeline", "payload": pipeline},
    #     {"field": "state.addMode", "payload": False},
    # ]
    # api.task.set_fields(task_id, fields)


@app.callback("preview_pipeline")
@sly.timeit
def preview_pipeline(api: sly.Api, task_id, context, state, app_logger):
    pass


import pickle


def main():
    data = {}
    state = {}

    cache_images(app.public_api, project_id)
    ui.init_input_project(app.public_api, data, project_info)
    ui.init_pipeline(data, state)
    ui.init_augs_configs(data, state)
    ui.init_preview(data, state)
    ui.init_docs(data)

    #TODO: for debug
    state["addMode"] = True
    state["category"] = "arithmetic"
    state["aug"] = "ImpulseNoise"

    app.run(data=data, state=state)

# check and fix build_pipeline
# rename augVModels -> params
# restore-default on client
# @TODO: random_order flag (shuffle flag to entire pipeline)
if __name__ == "__main__":
    sly.main_wrapper("main", main)

