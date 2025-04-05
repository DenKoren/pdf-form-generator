class Error(Exception):
    pass


class FormNotFound(Error):
    def __init__(self, name: str, file_path: str = "<stream>"):
        super(FormNotFound, self).__init__(
            f"definition for form '{name}' not found in '{file_path}'"
        )
