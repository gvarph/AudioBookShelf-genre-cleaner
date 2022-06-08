import sys
import typing


from replaceFile import get_replace

from ABSapiClient import ABSLibrary


def get_basic_info() -> typing.Tuple[str, str, str]:
    if len(sys.argv) > 1:
        baseURL = sys.argv[1]
    else:
        print("Enter ABS URL: ", end="")
        baseURL = input()
    baseURL += "/api"

    if len(sys.argv) > 2:
        library = sys.argv[2]
    else:
        print("Enter Library ID: ", end="")
        library = input()

    if len(sys.argv) > 3:
        api_token = sys.argv[3]
    else:
        print("Enter API Token: ", end="")
        api_token = input()

    return baseURL, library, api_token


def print_progress(progress: int, total: int):
    print(f"\rProgress: {progress}/{total}", end="")


if __name__ == "__main__":
    baseURL, library, api_token = get_basic_info()

    lib = ABSLibrary(baseURL, library, api_token)

    all_audiobooks = lib.get_all_audiobooks()

    replace = get_replace(lib, "replace.json")

    existing_genres = lib.get_genres()

    keys = list(replace.keys())

    for key in keys:
        if key not in existing_genres:
            del replace[key]

    if len(replace) == 0:
        print("Nothing to replace")
        exit(0)

    for key, value in replace.items():
        print('"' + key + '"' + str(value))

    print("Continue? (y/n)")

    while True:
        answer = input()
        if answer == "y":
            break
        elif answer == "n":
            exit(0)
        else:
            print("Please enter y or n")

    new_all_audiobooks = {}

    count = 0
    total = len(all_audiobooks)
    posted = False
    for audiobook in all_audiobooks:
        count += 1
        had_to_replace = False

        payload = {}

        id = audiobook["id"]
        media = audiobook["media"]
        metadata = media["metadata"]
        if "genres" in metadata:
            genres = metadata["genres"]
            new_genres = []
            for genre in genres:
                genre = genre.strip()
                if genre in replace:
                    had_to_replace = True
                    rep = replace[genre]
                    if rep.remove:
                        continue  # skip this genre
                    for g in rep.replace_with:
                        if g not in new_genres:
                            new_genres.append(g)
                elif genre not in new_genres:
                    new_genres.append(genre)
            payload = {"metadata": {"genres": new_genres}}

        if had_to_replace:
            data = payload

            response = lib.patch_media_metadata(id, data)
            print_progress(count, total)
            if response.status_code == 200:
                pass
            else:
                print("\tFailed to patch " + id)
                print(response.text)

        elif count == total:
            print_progress(count, total)
            break
