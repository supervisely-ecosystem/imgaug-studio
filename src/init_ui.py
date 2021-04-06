import os
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


def get_empty_gallery(meta: sly.ProjectMeta = sly.ProjectMeta()):
    CNT_GRID_COLUMNS = 2
    empty_gallery = {
        "content": {
            "projectMeta": sly.ProjectMeta().to_json(),
            "annotations": {},
            "layout": [[] for i in range(CNT_GRID_COLUMNS)]
        },
        "previewOptions": {
            "opacity": 0.1,
            "enableZoom": True,
            "resizeOnZoom": True,
            "showOpacityInHeader": True,
        },
        "options": {
            "enableZoom": True,
            "syncViews": True,
            "showPreview": False,
            "selectable": False,
            "opacity": 0.1,
            "showOpacityInHeader": True,
            # "viewHeight": 450
        }
    }
    return CNT_GRID_COLUMNS, empty_gallery


def init_preview(data, state):
    _, data["gallery"] = get_empty_gallery()
    state["previewLoading"] = False
    data["previewPy"] = None
    data["pyViewOptions"] = {
        "mode": 'ace/mode/python',
        "showGutter": False,
        "readOnly": True,
        "maxLines": 10,
        "highlightActiveLine": False
    }

    #@TODO: delete
    state["num"] = 5
    state["fl"] = 0.3


def init_docs(data):
    data["docs"] = {}

    from src.allowed_augs import augs_modules
    for module_name, methods in augs_modules.items():
        for method in methods:
            doc_path = f"../html_kit/{method.__name__}.html"
            with open(doc_path, 'r') as file:
                data["docs"][method.__name__] = file.read()
