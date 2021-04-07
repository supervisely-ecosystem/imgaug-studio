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


@app.callback("preview")
@sly.timeit
def preview(api: sly.Api, task_id, context, state, app_logger):
    aug_info = ui_augs.get_aug_info(state)
    aug = imgaug_utils.build(aug_info)

    img_info, img = get_random_image(api)
    res_img = imgaug_utils.apply(aug, img)
    file_info = save_preview_image(api, task_id, res_img)
    gallery = ui.get_gallery(urls=[img_info.full_storage_url, file_info.full_storage_url])

    fields = [
        {"field": "data.gallery", "payload": gallery},
        {"field": "state.previewLoading", "payload": False},
        {"field": "data.previewPy", "payload": aug_info["python"]},
    ]
    api.task.set_fields(task_id, fields)


@app.callback("add_to_pipeline")
@sly.timeit
def add_to_pipeline(api: sly.Api, task_id, context, state, app_logger):
    aug_info = ui_augs.get_aug_info(state)

    print(json.dumps(aug_info, indent=4))
    pipeline.append(aug_info)

    fields = [
        {"field": "data.pipeline", "payload": pipeline},
        {"field": "state.addMode", "payload": False},
    ]
    api.task.set_fields(task_id, fields)


@app.callback("preview_pipeline")
@sly.timeit
def preview_pipeline(api: sly.Api, task_id, context, state, app_logger):
    pass


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
# restore-default on client
# @TODO: random_order flag (shuffle flag to entire pipeline)
if __name__ == "__main__":
    sly.main_wrapper("main", main)

