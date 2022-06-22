import requests
import urllib.parse
from util import print_progress

from replaceFile import get_replace, save_json


class ABSLibrary:

    all_audiobooks = None

    def __init__(self, baseURL, library, api_token):
        self.baseURL = baseURL
        self.baseURLwAPI = baseURL + "/api"
        self.library = library
        self.api_token = api_token

    def get_response(self, url: str) -> requests.Response:
        response = requests.get(
            url, headers={"Authorization": "Bearer " + self.api_token}
        )
        return response

    def get_all_audiobooks(self) -> list[dict]:
        if self.all_audiobooks is not None:
            return self.all_audiobooks

        response = self.get_response(
            self.baseURLwAPI + "/libraries/" + self.library + "/items"
        )
        if response.status_code == 200:
            response_json = response.json()
            audiobooks = response_json["results"]
            return audiobooks
        else:
            print("Error: " + response.text)
            exit(1)

    def get_book_ids(self) -> list[str]:
        book_ids = []
        for book in self.audiobooks:
            book_ids.append(book["id"])
        print("Found " + str(len(book_ids)) + " audiobooks")
        return book_ids

    def get_genres(self) -> list[str]:
        genres = set()
        all_audiobooks = self.get_all_audiobooks()
        for book in all_audiobooks:
            metadata = book["media"]["metadata"]
            if "genres" in metadata:
                for genre in metadata["genres"]:
                    genres.add(genre)
        return genres

    def patch_media(self, book_id: str, json: dict) -> requests.Response:
        url = self.baseURLwAPI + "/items/" + book_id + "/media"

        response = requests.patch(
            url,
            verify=True,
            headers={"Authorization": "Bearer " + self.api_token},
            json=json,
        )
        return response

    def genre_cleanup(self):
        replace = get_replace(self, "replace.json")

        all_audiobooks = self.get_all_audiobooks()

        existing_genres = self.get_genres()
        existing_genres = [genre.strip() for genre in existing_genres]

        keys = list(replace.keys())

        for key in keys:
            key = key.strip()
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

        count = 0
        total = len(all_audiobooks)
        for audiobook in all_audiobooks:
            count += 1
            had_to_replace = False

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

            if had_to_replace:

                response = self.patch_media(id, {"metadata": {"genres": new_genres}})
                print_progress(count, total)
                if response.status_code == 200:
                    pass
                else:
                    print("\tFailed to patch " + id)
                    print(response.text)

            elif count == total:
                print_progress(count, total)
                break
        return

    def find_dupes_by_ASIN(self):
        # throw a not implemented error
        print("Finding duplicates by ASIN")
        all_audiobooks = self.get_all_audiobooks()
        ASINs = {}  # ASIN -> [audiobook_id]

        for audiobook in all_audiobooks:
            media = audiobook["media"]
            metadata = media["metadata"]
            if "asin" in metadata and metadata["asin"] is not None:
                asin = metadata["asin"]
                ab = {"id": audiobook["id"], "title": metadata["title"]}
                if asin in ASINs:
                    ASINs[asin].append(ab)
                else:
                    ASINs[asin] = [ab]

        for asin, abs in ASINs.items():
            if len(abs) > 1:
                names = set()
                for ab in abs:
                    names.add(ab["title"])

                if len(names) == 1:
                    print(str(asin) + ": " + names.pop())
                else:
                    print(str(asin) + ": " + str(", ".join(names)))

                for ab in abs:
                    print("\t" + self.baseURL + "/item/" + ab["id"])

    def rebuild_titles_by_ASIN(self):
        print("Getting new titles for audiobooks with ASIN")

        all_abs = self.get_all_audiobooks()

        edited = 0
        count = 0

        abs_with_asin = [
            abs
            for abs in all_abs
            if "media" in abs
            and "metadata" in abs["media"]
            and "asin" in abs["media"]["metadata"]
            and abs["media"]["metadata"]["asin"] is not None
        ]
        total = len(abs_with_asin)
        print(str(total) + " out of " + str(len(all_abs)) + " audiobooks have ASINs")
        for ab in abs_with_asin:
            asin = ab["media"]["metadata"]["asin"]

            old_title = ab["media"]["metadata"]["title"]

            query = "https://audiobooks.gvarph.com/api/search/books"

            response = requests.get(
                "https://api.audnex.us/books/" + urllib.parse.quote(asin)
            )

            if not response.status_code == 200:
                print("\t" + ab["id"] + " " + asin + " " + str(response))
                continue

            new_title = response.json()["title"]

            if not new_title == old_title:
                patch_response = self.patch_media(
                    ab["id"], {"metadata": {"title": new_title}}
                )
                if patch_response.status_code == 200:
                    edited += 1
                else:
                    print("Failed to patch " + ab["id"])
                    print(patch_response.text)
            count += 1
            print_progress(count, total)

        print("\n\nPatched " + str(edited) + " audiobooks")
        return

    def cleanse_if_asin(self):
        print("Cleansing audiobooks with ASIN")

        all_abs = self.get_all_audiobooks()

        edited = 0
        count = 0

        abs_with_asin = [
            abs
            for abs in all_abs
            if "media" in abs
            and "metadata" in abs["media"]
            and "asin" in abs["media"]["metadata"]
            and abs["media"]["metadata"]["asin"] is not None
        ]
        total = len(abs_with_asin)
        print(str(total) + " out of " + str(len(all_abs)) + " audiobooks have ASINs")
        for ab in abs_with_asin:
            asin = ab["media"]["metadata"]["asin"]

            response = requests.get(
                "https://api.audnex.us/books/" + urllib.parse.quote(asin)
            )

            if not response.status_code == 200:
                print("\t" + ab["id"] + " " + asin + " " + str(response))
                continue

            patch_response = self.patch_media(
                ab["id"],
                {
                    "metadata": {
                        "authors": [],
                        "narrators": [],
                        "subtitle": None,
                        "genres": [],
                        "series": [],
                    }
                },
            )
            if patch_response.status_code == 200:
                edited += 1
            else:
                print("Failed to cleanse " + ab["id"])
                print(patch_response.text)
            count += 1
            print_progress(count, total)

        print("\n\cleansed " + str(edited) + " audiobooks")
        return
