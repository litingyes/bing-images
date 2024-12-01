from curses.ascii import alt
from enum import Enum
from json import loads
from os import environ, path
from pathlib import Path
from algoliasearch.search.client import SearchClientSync
from shared import BING_DOMAIN, get_database_path

INDEX_NAME = "website"

application_key = environ.get("ALGOLIA_APPLICATION_ID")
api_key = environ.get("ALGOLIA_WRITE_API_KEY")


class TYPES(Enum):
    IMAGE = "image"
    EMOJI = 'emoji'


class LANGS(Enum):
    EN_US = "en-US"
    ZN_CN = "zh-CN"


class TAGS(Enum):
    # type
    IMAGE = "image"

    # langs
    EN_US = "en-US"
    ZN_CN = "zh-CN"

    # module
    DAILY_WALLPAPER = "daily-wallpaper"
    SEARCH_WALLPAPER = "search-wallpaper"


def wrap_add_object(record):
    return {"action": "addObject", "body": record}

def add_records(records):
    client = SearchClientSync(application_key, api_key)
    client.batch(INDEX_NAME, {"requests": list(map(wrap_add_object, records))})
    client.close()
    


def reset_records():
    client = SearchClientSync(application_key, api_key)
    client.clear_objects(INDEX_NAME)
    client.close()

    database_path = get_database_path()
    records = []

    daily_wallpaper_dir = path.join(database_path, "bing", "daily-wallpaper")
    for lang in [TAGS.EN_US.value, TAGS.ZN_CN.value]:
        for file in Path(path.join(daily_wallpaper_dir, lang)).rglob("*.json"):
            with open(file, "r") as f:
                data = loads(f.read())
                for item in data:
                    record = {
                        "type": TYPES.IMAGE.value,
                        "url": BING_DOMAIN + item["url"],
                        "alt": item["title"],
                        "tags": [TAGS.IMAGE.value, lang, TAGS.DAILY_WALLPAPER.value],
                    }
                    records.append(record)

    search_wallpaper_dir = path.join(database_path, "bing", "search-wallpaper")
    for file in Path(search_wallpaper_dir).rglob("*.json"):
        with open(file, "r") as f:
            data = loads(f.read())
            for item in data:
                record = {
                    "type": TYPES.IMAGE.value,
                    "url": item["thumbnail"]["thumbnailUrl"],
                    "alt": item["displayText"],
                    "tags": [TAGS.IMAGE.value, TAGS.EN_US.value, TAGS.SEARCH_WALLPAPER.value],
                }
                records.append(record)

    trending_images_dir = path.join(database_path, "bing", "trending-images")
    for lang in [TAGS.EN_US.value, TAGS.ZN_CN.value]:
        with open(path.join(trending_images_dir, lang + ".json"), "r") as f:
            data = loads(f.read())
            for group in data:
                for item in group["tiles"]:
                    record = {
                        "type": TYPES.IMAGE.value,
                        "url": item["image"]["contentUrl"],
                        "alt": item["query"]["displayText"],
                        "tags": [
                            TAGS.IMAGE.value,
                            lang,
                            TAGS.SEARCH_WALLPAPER.value,
                        ],
                    }
                    records.append(record)

    add_records(records)
    

if __name__ == "__main__":
    reset_records()
    
