# https://www.youtube.com/watch?v=DnKxKFXB4NQ&list=LL&index=6&ab_channel=mCoding
# from functools import cache, lru_cache
import random
import supervisely as sly


images_info = {}
all_images = []


def cache_images(api: sly.Api, project_id):
    sly.logger.debug(f"Caching triggered for project {project_id}")
    for dataset in api.dataset.get_list(project_id, recursive=True):
        sly.logger.debug(f"Caching images for dataset with ID: {dataset.id}")
        images_info[dataset.name] = api.image.get_list(dataset.id)
        all_images.extend(images_info[dataset.name])
        sly.logger.debug(f"Now cache contains {len(all_images)} images from dataset.")

    sly.logger.info(f"Total images cached: {len(all_images)}")


# @lru_cache(maxsize=5)
def _get_image_by_id(api: sly.Api, image_id):
    img = api.image.download_np(image_id)
    return img


def get_random_image(api: sly.Api):
    sly.logger.debug(
        f"Getting random image from cache. Cached images: {len(all_images)}"
    )
    image_info = random.choice(all_images)
    return image_info, _get_image_by_id(api, image_info.id)
