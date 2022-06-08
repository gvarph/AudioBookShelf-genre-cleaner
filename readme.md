# About

This is but a simple script used to clean up audiobook genres on AudioBookShelf

## Usage

1) Download the script
2) run `pip install -r requirements.txt` 
3) generate AudioBookShelf API key (ABS -> Settings -> Users -> select a user -> API key)
4) run the script once (using `python3 ABScleaner.py <url> <library> <Api key>`). This will create a new file called replace.json containing all of your existing book genres.
5) edit the replace.json file with the genres you want to replace (see example below)

```json
 { 
    "Fantasy": { //will keep the Fantasy genre
        "remove": false,
        "replace_with": []
    },
    "Audiobooks": { //will remove the Audiobooks genre from any book
        "remove": true,
        "replace_with": []
    },
    "Sci-fi": { // will replace the Sci-fi genre with 'Science Fiction'
        "remove": false,
        "replace_with": ["Science Fiction"]
    },
    "Sci-fi & Fantasy": { // will remove the genre called 'Sci-fi & Fantasy'
        "remove": false,  // and replace it with both 'Sci-fi' and 'Fantasy'
        "replace_with": ["Science Fiction", "Fantasy"]
    }
}
```

7) run the script again. This will update your book genres with the new ones.
