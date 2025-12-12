import os
import json
import time

import supervisely as sly
from supervisely.app.v1.app_service import AppService

import ui
from cache import get_random_image, cache_images
import ui_augs


app: AppService = AppService()

team_id = int(os.environ["context.teamId"])
workspace_id = int(os.environ["context.workspaceId"])
project_id = int(os.environ["modal.state.slyProjectId"])

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
    remote_path = os.path.join(f"/imgaug_studio/{task_id}", f"last_preview.png")
    sly.image.write(local_path, img)
    if api.file.exists(team_id, remote_path):
        api.file.remove(team_id, remote_path)
    file_info = api.file.upload(team_id, local_path, remote_path)
    return file_info


def rename_meta_and_annotations(
    meta: sly.ProjectMeta, ann: sly.Annotation, suffix="original"
):
    def _get_new_name(current_name):
        return f"{current_name}-{suffix}"

    new_classes = []
    for obj_class in meta.obj_classes:
        obj_class: sly.ObjClass
        new_classes.append(obj_class.clone(name=_get_new_name(obj_class.name)))
    new_meta = meta.clone(obj_classes=sly.ObjClassCollection(new_classes))

    new_labels = []
    for label in ann.labels:
        dest_name = _get_new_name(label.obj_class.name)
        dest_class = new_meta.get_obj_class(dest_name)
        new_labels.append(label.clone(obj_class=dest_class))
    new_ann = ann.clone(labels=new_labels)
    return new_meta, new_ann


def preview_augs(api: sly.Api, task_id, augs, infos, py_code=None):
    img_info, img = get_random_image(api)
    ann_json = api.annotation.download(img_info.id).annotation
    ann = sly.Annotation.from_json(ann_json, meta)

    try:
        res_meta, res_img, res_ann = sly.imgaug_utils.apply(augs, meta, img, ann)
    except ValueError as e:
        if str(e) == "cannot convert float NaN to integer":
            e.args = ("Please check the values of the augmentation parameters",)
            raise e
        else:
            raise e
    file_info = save_preview_image(api, task_id, res_img)

    # rename polygonal labels in existing annotation to keep them in gallery in before section
    # cheat code ############################################
    _labels_new_classes = []
    _new_classes = {}
    for label in ann.labels:
        label: sly.Label
        if type(label.obj_class.geometry_type) is sly.Rectangle:
            new_name = f"{label.obj_class.name}_polygon_for_gallery"
            if new_name not in _new_classes:
                _new_classes[new_name] = label.obj_class.clone(name=new_name)
            _labels_new_classes.append(label.clone(obj_class=_new_classes[new_name]))
        else:
            _labels_new_classes.append(label.clone())
    _meta_renamed_polygons = sly.ProjectMeta(
        obj_classes=sly.ObjClassCollection(list(_new_classes.values()))
    )
    gallery_meta = res_meta.merge(_meta_renamed_polygons)
    # cheat code ############################################

    gallery, sync_keys = ui.get_gallery(
        project_meta=gallery_meta,
        urls=[img_info.path_original, file_info.storage_path],
        card_names=["original", "augmented"],
        img_labels=[_labels_new_classes, res_ann.labels],
    )
    fields = [
        {"field": "data.gallery", "payload": gallery},
        {"field": "state.galleryOptions.syncViewsBindings", "payload": sync_keys},
        {"field": "state.previewPipelineLoading", "payload": False},
        {"field": "state.previewAugLoading", "payload": False},
    ]
    if len(infos) == 1 and py_code is None:
        fields.append({"field": "state.previewPy", "payload": infos[0]["python"]})
    else:
        if py_code is None:
            py_code = sly.imgaug_utils.pipeline_to_python(infos, random_order=False)
        fields.append({"field": "state.previewPy", "payload": py_code})
    api.task.set_fields(task_id, fields)


@app.callback("clear_pipeline")
@sly.timeit
@ui.handle_exceptions(app.task_id, app.public_api)
def clear_pipeline(api: sly.Api, task_id, context, state, app_logger):
    fields = [
        {"field": "data.pipeline", "payload": []},
        {"field": "state.addMode", "payload": False},
        {"field": "state.previewPy", "payload": None},
        {"field": "state.randomOrder", "payload": False},
        {"field": "state.previewPipelineLoading", "payload": False},
        {"field": "state.previewAugLoading", "payload": False},
    ]
    api.task.set_fields(task_id, fields)


@app.callback("load_existing_pipeline")
@sly.timeit
@ui.handle_exceptions(app.task_id, app.public_api)
def load_existing_pipeline(api: sly.Api, task_id, context, state, app_logger):
    remote_path = state["pipelinePath"]
    local_path = os.path.join(app.data_dir, sly.fs.get_file_name_with_ext(remote_path))
    api.file.download(team_id, remote_path, local_path)
    config = sly.json.load_json_file(local_path)
    _ = sly.imgaug_utils.build_pipeline(
        config["pipeline"], config["random_order"]
    )  # validate
    global pipeline
    pipeline = config["pipeline"]

    fields = [
        {"field": "data.pipeline", "payload": config["pipeline"]},
        {"field": "state.addMode", "payload": False},
        {"field": "state.previewPy", "payload": None},
        {"field": "state.randomOrder", "payload": config["random_order"]},
    ]
    api.task.set_fields(task_id, fields)


@app.callback("preview")
@sly.timeit
@ui.handle_exceptions(app.task_id, app.public_api)
def preview(api: sly.Api, task_id, context, state, app_logger):
    aug_info = ui_augs.get_aug_info(state)
    aug = sly.imgaug_utils.build(aug_info)
    preview_augs(api, task_id, aug, [aug_info])


@app.callback("add_to_pipeline")
@sly.timeit
@ui.handle_exceptions(app.task_id, app.public_api)
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
@ui.handle_exceptions(app.task_id, app.public_api)
def preview_pipeline(api: sly.Api, task_id, context, state, app_logger):
    random_order = False
    if len(pipeline) > 1:
        random_order = state["randomOrder"]
    augs = sly.imgaug_utils.build_pipeline(pipeline, random_order)
    py_code = sly.imgaug_utils.pipeline_to_python(pipeline, random_order)
    preview_augs(api, task_id, augs, pipeline, py_code)


@app.callback("export_pipeline")
@sly.timeit
@ui.handle_exceptions(app.task_id, app.public_api)
def export_pipeline(api: sly.Api, task_id, context, state, app_logger):
    api.task.set_field(task_id, "state.exporting", True)

    random_order = False
    if len(pipeline) > 1:
        random_order = state["randomOrder"]

    name = state["saveName"]
    py_code = sly.imgaug_utils.pipeline_to_python(pipeline, random_order)
    py_path = os.path.join(app.data_dir, f"{name}.py")
    with open(py_path, "w") as text_file:
        text_file.writelines(py_code)

    json_path = os.path.join(app.data_dir, f"{name}.json")
    res_json = {"pipeline": pipeline, "random_order": random_order}
    sly.json.dump_json_file(res_json, json_path)

    remote_py_path = os.path.join(state["saveDir"], f"{name}.py")
    remote_json_path = os.path.join(state["saveDir"], f"{name}.json")

    if api.file.exists(team_id, remote_py_path):
        remote_py_path = api.file.get_free_name(team_id, remote_py_path)
    if api.file.exists(team_id, remote_json_path):
        remote_json_path = api.file.get_free_name(team_id, remote_json_path)

    infos = api.file.upload_bulk(
        team_id, [py_path, json_path], [remote_py_path, remote_json_path]
    )
    fields = [
        {"field": "state.exporting", "payload": False},
        {"field": "state.savedUrl", "payload": api.file.get_url(infos[1].id)},
        {"field": "state.savedPath", "payload": infos[1].path},
    ]
    api.task.set_fields(task_id, fields)


@app.callback("delete_aug")
@sly.timeit
@ui.handle_exceptions(app.task_id, app.public_api)
def delete_aug(api: sly.Api, task_id, context, state, app_logger):
    global pipeline
    index = state["augIndex"]
    if 0 <= index < len(pipeline):
        del pipeline[index]
    else:
        sly.logger.info("Item already deleted.")
        return
    fields = [
        {"field": "data.pipeline", "payload": pipeline},
        {"field": "data.augIndex", "payload": None},
    ]
    api.task.set_fields(task_id, fields)


@app.callback("move_aug_up")
@sly.timeit
@ui.handle_exceptions(app.task_id, app.public_api)
def move_aug_up(api: sly.Api, task_id, context, state, app_logger):
    global pipeline
    index = state["augIndex"]
    if index is not None and index > 0:
        a = pipeline[index - 1]
        pipeline[index - 1] = pipeline[index]
        pipeline[index] = a
    fields = [
        {"field": "data.pipeline", "payload": pipeline},
        {"field": "data.augIndex", "payload": None},
    ]
    api.task.set_fields(task_id, fields)


@app.callback("move_aug_down")
@sly.timeit
@ui.handle_exceptions(app.task_id, app.public_api)
def move_aug_down(api: sly.Api, task_id, context, state, app_logger):
    global pipeline
    index = state["augIndex"]
    if index is not None and index < len(pipeline) - 1:
        a = pipeline[index + 1]
        pipeline[index + 1] = pipeline[index]
        pipeline[index] = a
    fields = [
        {"field": "data.pipeline", "payload": pipeline},
        {"field": "data.augIndex", "payload": None},
    ]
    api.task.set_fields(task_id, fields)


def main():
    data = {}
    state = {}

    cache_images(app.public_api, project_id)
    ui.init_input_project(app.public_api, data, project_info)
    ui.init_pipeline(data, state)
    ui.init_augs_configs(data, state)
    ui.init_preview(data, state)
    ui.init_docs(data)
    ui.init_export(data, state, app.task_id)

    # # @TODO: for debug
    # state["addMode"] = True
    # state["category"] = "size"
    # state["aug"] = "PadToFixedSize"

    app.run(data=data, state=state)


# @TODO: add resize
if __name__ == "__main__":
    sly.main_wrapper("main", main)
