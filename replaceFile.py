from dataclasses import dataclass
import json

from ABSapiClient import ABSLibrary


@dataclass
class replaceItem:
    remove: bool
    replace_with: list[str]

    def __str__(self):
        if self.remove:
            return " will be removed"
        elif len(self.replace_with) > 0:
            return " will be replaced with " + str(self.replace_with)
        else:
            return " will be kept"


def save_json(filename: str, json_data: dict) -> None:
    with open(filename, "w") as f:
        f.write(json.dumps(json_data, indent=4))


def gen_new_replace_file(library: ABSLibrary, fileName) -> None:
    genres = {}
    existing_genres = library.get_genres()
    for genre in existing_genres:
        new_genre = {}
        new_genre["remove"] = False
        new_genre["replace_with"] = []
        genres[genre.strip()] = new_genre

    save_json(fileName, genres)


def get_replace(library: ABSLibrary, filename: str) -> list[replaceItem]:

    try:
        with open(filename, "r") as f:
            replace = json.loads(f.read())
    except FileNotFoundError:
        print(filename + " not found, generating new one based on existing audiobooks")
        gen_new_replace_file(library, filename)
        print("Please edit the file, save it and run the script again")
        exit(0)
    except json.decoder.JSONDecodeError:
        print("file is not a valid json file")
        exit(1)

    to_replace = {}
    for genre in replace:
        remove = replace[genre]["remove"]
        replace_with = replace[genre]["replace_with"]
        if remove or len(replace_with) > 0:
            to_replace[genre] = replaceItem(remove, replace_with)

    return to_replace
