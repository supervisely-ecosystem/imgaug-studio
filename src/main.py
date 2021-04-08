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


def save_preview_image(api: sly.Api, task_id, img):
    local_path = os.path.join(vis_dir, f"last_preview.png")
    remote_path = os.path.join(f"/imgaug-studio/{task_id}", f"last_preview.png")
    sly.image.write(local_path, img)
    if api.file.exists(team_id, remote_path):
        api.file.remove(team_id, remote_path)
    file_info = api.file.upload(team_id, local_path, remote_path)
    return file_info


def preview_augs(api: sly.Api, task_id, augs, infos, py_code=None):
    img_info, img = get_random_image(api)
    res_img = imgaug_utils.apply(augs, img)
    file_info = save_preview_image(api, task_id, res_img)
    gallery = ui.get_gallery(urls=[img_info.full_storage_url, file_info.full_storage_url])
    fields = [
        {"field": "data.gallery", "payload": gallery},
        {"field": "state.previewLoading", "payload": False},
    ]
    if len(infos) == 1 and py_code is None:
        fields.append({"field": "state.previewPy", "payload": infos[0]["python"]})
    else:
        if py_code is None:
            py_code = imgaug_utils.pipeline_to_python(infos, random_order=False)
        fields.append({"field": "state.previewPy", "payload": py_code})
    api.task.set_fields(task_id, fields)


@app.callback("preview")
@sly.timeit
def preview(api: sly.Api, task_id, context, state, app_logger):
    aug_info = ui_augs.get_aug_info(state)
    aug = imgaug_utils.build(aug_info)
    preview_augs(api, task_id, aug, [aug_info])


@app.callback("add_to_pipeline")
@sly.timeit
def add_to_pipeline(api: sly.Api, task_id, context, state, app_logger):
    aug_info = ui_augs.get_aug_info(state)
    pipeline.append(aug_info)

    fields = [
        {"field": "data.pipeline", "payload": pipeline},
        {"field": "state.addMode", "payload": False},
        {"field": "state.previewPy", "payload": None},
    ]
    api.task.set_fields(task_id, fields)


@app.callback("preview_pipeline")
@sly.timeit
def preview_pipeline(api: sly.Api, task_id, context, state, app_logger):
    random_order = False
    if len(pipeline) > 1:
        random_order = state["randomOrder"]
    augs = imgaug_utils.build_pipeline(pipeline, random_order)
    py_code = imgaug_utils.pipeline_to_python(pipeline, random_order=False)
    preview_augs(api, task_id, augs, pipeline, py_code)


def main():
    data = {}
    state = {}

    cache_images(app.public_api, project_id)
    ui.init_input_project(app.public_api, data, project_info)
    ui.init_pipeline(data, state)
    ui.init_augs_configs(data, state)
    ui.init_preview(data, state)
    ui.init_docs(data)

    #@TODO: for debug
    # state["addMode"] = True
    # state["category"] = "arithmetic"
    # state["aug"] = "ImpulseNoise"

    app.run(data=data, state=state)


if __name__ == "__main__":
    sly.main_wrapper("main", main)

