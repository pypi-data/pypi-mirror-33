try:
    from .librarian import Librarian
except (SystemError, ImportError):
    from librarian import Librarian

