import sys
import typing


from ABSapiClient import ABSLibrary


def get_basic_info() -> typing.Tuple[str, str, str]:
    if len(sys.argv) > 1:
        baseURL = sys.argv[1]
    else:
        print("Enter ABS URL: ", end="")
        baseURL = input()
    baseURL += ""

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


if __name__ == "__main__":

    baseURL, library, api_token = get_basic_info()

    lib = ABSLibrary(baseURL, library, api_token)

    print("What do you want to do?")
    print("1. Clean up genres")
    print("2. find duplicates")
    print("3. rebuild titles")
    print("x. Exit")

    a = True
    while a:
        a = False
        answer = input()

        if answer == "1":
            lib.genre_cleanup()

        elif answer == "2":
            lib.find_dupes_by_ASIN()

        elif answer == "3":
            lib.rebuild_titles_by_ASIN()
        elif answer == "4":
            lib.cleanse_if_asin()

        elif answer == "x":
            exit(0)

        else:
            a = True
