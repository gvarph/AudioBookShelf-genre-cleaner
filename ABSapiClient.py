import requests


class ABSLibrary:
    # URL to ABS
    baseURL = ""

    # Library to Use
    library = ""

    # ABS -> Settings -> Users -> select user -> "API Token"
    api_token = ""

    all_audiobooks = None

    def __init__(self, baseURL, library, api_token):
        self.baseURL = baseURL
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
            self.baseURL + "/libraries/" + self.library + "/items"
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

    def patch_media_metadata(self, book_id: str, payload: dict) -> requests.Response:
        url = self.baseURL + "/items/" + book_id + "/media"

        response = requests.patch(
            url,
            verify=True,
            headers={"Authorization": "Bearer " + self.api_token},
            json={"metadata": {"genres": payload.get("metadata").get("genres")}},
        )
        return response
