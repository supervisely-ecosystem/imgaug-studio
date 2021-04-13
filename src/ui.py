import os
from collections import defaultdict
import supervisely_lib as sly

augs_configs = sly.json.load_json_file("augs.json")


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
    data["pipeline"] = [
        # "iaa.imgcorruptlike.GaussianBlur(severity=(1, 1))",
        # "iaa.imgcorruptlike.GaussianBlur(severity=(2, 2))",
        # "iaa.imgcorruptlike.GaussianBlur(severity=(3, 3))",
    ]
    state["addMode"] = False
    state["randomOrder"] = False


def get_empty_gallery(meta: sly.ProjectMeta = sly.ProjectMeta()):
    CNT_GRID_COLUMNS = 2
    empty_gallery = {
        "content": {
            "projectMeta": meta.to_json(),
            "annotations": {},
            "layout": [[] for i in range(CNT_GRID_COLUMNS)]
        },
        "previewOptions": {
            "opacity": 0.5,
            "enableZoom": True,
            "resizeOnZoom": True,
            "showOpacityInHeader": True,
        },
        "options": {
            "enableZoom": True,
            "syncViews": True,
            "showPreview": False,
            "selectable": False,
            "opacity": 0.5,
            "showOpacityInHeader": True,
            # "viewHeight": 450
        }
    }
    return CNT_GRID_COLUMNS, empty_gallery


def init_preview(data, state):
    _, data["gallery"] = get_empty_gallery()
    state["previewLoading"] = False
    state["previewPy"] = None
    data["pyViewOptions"] = {
        "mode": 'ace/mode/python',
        "showGutter": False,
        "readOnly": True,
        "maxLines": 50,
        "highlightActiveLine": False
    }
    state["sometimes"] = False


def init_docs(data):
    data["docs"] = defaultdict(dict)

    from src.allowed_augs import augs_modules
    for module_name, methods in augs_modules.items():
        for method in methods:
            doc_path = f"../html_kit/{module_name}.{method.__name__}.html".lower()
            with open(doc_path, 'r') as file:
                data["docs"][module_name][method.__name__] = file.read()


def get_gallery(project_meta: sly.ProjectMeta, urls, img_labels=None):
    if img_labels is None:
        img_labels = [[]] * len(urls)

    if len(urls) % 2 != 0:
        raise ValueError("Gallery only for image pairs")

    CNT_GRID_COLUMNS, gallery = get_empty_gallery(project_meta)

    grid_annotations = {}
    grid_layout = [[] for i in range(CNT_GRID_COLUMNS)]
    sync_keys = [[] for i in range(int((len(urls) / 2)))]
    for idx, (image_url, labels) in enumerate(zip(urls, img_labels)):
        grid_annotations[str(idx)] = {
            "url": image_url,
            "figures": [label.to_json() for label in labels]
        }
        grid_layout[idx % CNT_GRID_COLUMNS].append(str(idx))
        sync_keys[int(idx / 2)].append(str(idx))

    gallery["content"]["layout"] = grid_layout
    gallery["content"]["annotations"] = grid_annotations
    gallery["options"]["syncViewsBindings"] = sync_keys

    return gallery


def init_export(data, state, task_id):
    state["saveMode"] = False
    state["saveDir"] = f"/imgaug_studio/"
    state["saveName"] = f"{task_id}_my_pipeline"
    state["exporting"] = False
    state["savedUrl"] = None
    state["savedPath"] = None