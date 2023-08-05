from context import librarian

lib = librarian.Librarian()

alink = 'https://www.bloomberg.com/canada'
lib.get(alink)
lib.remove(alink)
