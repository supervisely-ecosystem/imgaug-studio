import os
import supervisely_lib as sly


def init_input_project(api: sly.Api, data: dict, project_info):
    data["projectId"] = project_info.id
    data["projectName"] = project_info.name
    data["projectPreviewUrl"] = api.image.preview_url(project_info.reference_image_url, 100, 100)
    data["projectItemsCount"] = project_info.items_count


def init_augs_configs(data: dict, state: dict):
    augs_configs = sly.json.load_json_file("augs.json")
    data["categories"] = list(augs_configs.keys())
    state["category"] = data["categories"][0]

    state["aug"] = None

    augs_list = {}
    for category, augs in augs_configs.items():
        augs_list[category] = list(augs.keys())
    data["augs"] = augs_list

    data["config"] = augs_configs
