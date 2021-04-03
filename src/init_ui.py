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


def init_pipeline(data, state):
    data["pipeline"] = [
        "iaa.imgcorruptlike.GaussianBlur(severity=(1, 5))"
    ]