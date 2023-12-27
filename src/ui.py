import os
from collections import defaultdict
import supervisely as sly
import functools
from pathlib import Path
import sys
from allowed_augs import augs_modules

root_source_path = str(Path(sys.argv[0]).parents[1])
augs_configs = sly.json.load_json_file(os.path.join(root_source_path, "src/augs.json"))


def init_input_project(api: sly.Api, data: dict, project_info):
    data["projectId"] = project_info.id
    data["projectName"] = project_info.name
    data["projectPreviewUrl"] = api.image.preview_url(project_info.reference_image_url, 100, 100)
    data["projectItemsCount"] = project_info.items_count


def init_augs_configs(data: dict, state: dict):
    data["categories"] = list(augs_configs.keys())
    state["category"] = data["categories"][0]

    state["aug"] = None
    state["augVModels"] = {}

    augs_list = {}
    for category, augs in augs_configs.items():
        augs_list[category] = list(augs.keys())
        state["augVModels"][category] = {}
        for aug_name, info in augs.items():
            state["augVModels"][category][aug_name] = {}
            for param in info["params"]:
                state["augVModels"][category][aug_name][param["pname"]] = param["default"]

    data["augs"] = augs_list
    data["config"] = augs_configs
    state["previewCount"] = 1

    state["sometimes"] = False
    state["sometimesP"] = 0.5


def init_pipeline(data, state):
    state["initMode"] = "new"
    state["pipelinePath"] = ""  # @TODO: for debug "/complex-07-fliplr.json"

    data["pipeline"] = []
    state["addMode"] = False
    state["randomOrder"] = False
    state["augIndex"] = None

    state["previewPipelineLoading"] = False


def get_empty_gallery(meta: sly.ProjectMeta = sly.ProjectMeta()):
    CNT_GRID_COLUMNS = 2
    empty_gallery = {
        "content": {
            "projectMeta": meta.to_json(),
            "annotations": {},
            "layout": [[] for i in range(CNT_GRID_COLUMNS)]
        },
    }
    return CNT_GRID_COLUMNS, empty_gallery


def init_preview(data, state):
    _, data["gallery"] = get_empty_gallery()
    state["previewPy"] = None
    data["pyViewOptions"] = {
        "mode": 'ace/mode/python',
        "showGutter": False,
        "readOnly": True,
        "maxLines": 50,
        "highlightActiveLine": False
    }
    state["sometimes"] = False

    state["galleryPreviewOptions"] = {
        "opacity": 0.5,
        "enableZoom": True,
        "resizeOnZoom": True,
        "showOpacityInHeader": True,
    },
    state["galleryOptions"] = {
        "enableZoom": True,
        "syncViews": True,
        "showPreview": False,
        "selectable": False,
        "opacity": 0.5,
        "showOpacityInHeader": True,
        # "viewHeight": 450,
    }
    state["showError"] = False
    data["error"] = None
    state["previewAugLoading"] = False


def init_docs(data):
    data["docs"] = defaultdict(dict)

    for module_name, methods in augs_modules.items():
        for method in methods:
            doc_path = os.path.join(root_source_path, f"html_kit/{module_name}.{method.__name__}.html".lower())
            with open(doc_path, 'r') as file:
                data["docs"][module_name][method.__name__] = file.read()


def get_gallery(project_meta: sly.ProjectMeta, urls, card_names, img_labels=None):
    if img_labels is None:
        img_labels = [[]] * len(urls)

    if len(urls) % 2 != 0:
        raise ValueError("Gallery only for image pairs")

    CNT_GRID_COLUMNS, gallery = get_empty_gallery(project_meta)

    grid_annotations = {}
    grid_layout = [[] for i in range(CNT_GRID_COLUMNS)]
    sync_keys = [[] for i in range(int((len(urls) / 2)))]
    for idx, (image_url, card_name, labels) in enumerate(zip(urls, card_names, img_labels)):
        grid_annotations[str(idx)] = {
            "url": image_url,
            "figures": [label.to_json() for label in labels],
            "info": {
                "title": card_name
            }
        }
        grid_layout[idx % CNT_GRID_COLUMNS].append(str(idx))
        sync_keys[int(idx / 2)].append(str(idx))

    gallery["content"]["layout"] = grid_layout
    gallery["content"]["annotations"] = grid_annotations
    return gallery, sync_keys


def init_export(data, state, task_id):
    state["saveMode"] = False
    state["saveDir"] = f"/imgaug_studio/"
    state["saveName"] = f"{task_id}_my_pipeline"
    state["exporting"] = False
    state["savedUrl"] = None
    state["savedPath"] = None


def handle_exceptions(task_id, api: sly.Api):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                fields = [
                    {"field": "data.error", "payload": None},
                    {"field": "state.showError", "payload": False},
                    {"field": "state.previewPipelineLoading", "payload": False},
                    {"field": "state.previewAugLoading", "payload": False},
                ]
                api.task.set_fields(task_id, fields)

                f(*args, **kwargs)
            except Exception as e:
                sly.logger.error(f"please, contact support: task_id={task_id}, {repr(e)}", exc_info=True, extra={
                    'exc_str': str(e),
                })
                fields = [
                    {"field": "data.error", "payload": repr(e)},
                    {"field": "state.showError", "payload": True},
                    {"field": "state.previewPipelineLoading", "payload": False},
                    {"field": "state.previewAugLoading", "payload": False},
                ]
                api.task.set_fields(task_id, fields)
        return wrapper
    return decorator