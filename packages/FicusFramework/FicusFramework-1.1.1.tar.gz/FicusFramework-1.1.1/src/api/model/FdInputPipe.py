from api.model.FdInputWrapper import FdInputWrapper


class FdInputPipe:
    """
    输入包装
    """
    __source_fd_codes = None

    def __init__(self, source_fd_codes):
        self.__source_fd_codes = source_fd_codes

    def list_source_fd_codes(self):
        return self.__source_fd_codes

    def get_fd(self, fd_code):
        return FdInputWrapper(fd_code)
