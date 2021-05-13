import os
import json
import time

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
    remote_path = os.path.join(f"/imgaug_studio/{task_id}", f"last_preview.png")
    sly.image.write(local_path, img)
    if api.file.exists(team_id, remote_path):
        api.file.remove(team_id, remote_path)
    file_info = api.file.upload(team_id, local_path, remote_path)
    return file_info


def rename_meta_and_annotations(meta: sly.ProjectMeta, ann: sly.Annotation, suffix="original"):
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

    det_meta, det_mapping = meta.to_detection_task(convert_classes=False)
    det_ann = ann.to_detection_task(det_mapping)
    ia_boxes = det_ann.bboxes_to_imgaug()

    seg_meta, seg_mapping = meta.to_segmentation_task()
    seg_ann = ann.to_nonoverlapping_masks(seg_mapping)
    seg_ann = seg_ann.to_segmentation_task()
    class_to_index = {obj_class.name: idx for idx, obj_class in enumerate(seg_meta.obj_classes, start=1)}
    index_to_class = {v: k for k, v in class_to_index.items()}
    ia_masks = seg_ann.masks_to_imgaug(class_to_index)

    res_meta = det_meta.merge(seg_meta)
    res_img, res_ia_boxes, res_ia_masks = imgaug_utils.apply(augs, img, ia_boxes, ia_masks)
    res_ann = sly.Annotation.from_imgaug(res_img,
                                         ia_boxes=res_ia_boxes, ia_masks=res_ia_masks,
                                         index_to_class=index_to_class, meta=res_meta)

    file_info = save_preview_image(api, task_id, res_img)
    gallery, sync_keys = ui.get_gallery(project_meta=res_meta,
                                        urls=[img_info.full_storage_url, file_info.full_storage_url],
                                        card_names=["original", "augmented"],
                                        img_labels=[ann.labels, res_ann.labels],
                                        )
    fields = [
        {"field": "data.gallery", "payload": gallery},
        {"field": "state.galleryOptions.syncViewsBindings", "payload": sync_keys},
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
@ui.handle_exceptions(app.task_id, app.public_api)
def preview(api: sly.Api, task_id, context, state, app_logger):
    aug_info = ui_augs.get_aug_info(state)
    aug = imgaug_utils.build(aug_info)
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
    augs = imgaug_utils.build_pipeline(pipeline, random_order)
    py_code = imgaug_utils.pipeline_to_python(pipeline, random_order)
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
    py_code = imgaug_utils.pipeline_to_python(pipeline, random_order)
    py_path = os.path.join(app.data_dir, f"{name}.py")
    with open(py_path, "w") as text_file:
        text_file.writelines(py_code)

    json_path = os.path.join(app.data_dir, f"{name}.json")
    res_json = {
        "pipeline": pipeline,
        "random_order": random_order
    }
    sly.json.dump_json_file(res_json, json_path)

    remote_py_path = os.path.join(state["saveDir"], f"{name}.py")
    remote_json_path = os.path.join(state["saveDir"], f"{name}.json")

    if api.file.exists(team_id, remote_py_path):
        remote_py_path = api.file.get_free_name(team_id, remote_py_path)
    if api.file.exists(team_id, remote_json_path):
        remote_json_path = api.file.get_free_name(team_id, remote_json_path)

    infos = api.file.upload_bulk(team_id, [py_path, json_path], [remote_py_path, remote_json_path])
    fields = [
        {"field": "state.exporting", "payload": False},
        # {"field": "state.saveMode", "payload": False},
        {"field": "state.savedUrl", "payload": api.file.get_url(infos[1].id)},
        {"field": "state.savedPath", "payload": infos[1].path}
    ]
    api.task.set_fields(task_id, fields)


@app.callback("delete_aug")
@sly.timeit
@ui.handle_exceptions(app.task_id, app.public_api)
def delete_aug(api: sly.Api, task_id, context, state, app_logger):
    global pipeline
    index = state["augIndex"]
    if index is not None:
        del pipeline[index]
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

# @TODO: load existing pipeline or start from scratch
# save: if name already exists
# @TODO: add resize
if __name__ == "__main__":
    sly.main_wrapper("main", main)
