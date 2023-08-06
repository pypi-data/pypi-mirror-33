import os.path

from ctypes import cdll, c_char_p, c_longlong, c_int, Structure

dll_path = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "go_get_urls.so"
go_linker = cdll.LoadLibrary(dll_path)


class GoString(Structure):
    _fields_ = [("p", c_char_p), ("n", c_longlong)]


go_linker.GetLinks.argtypes = [GoString, GoString, GoString, c_int, c_int]


def GetLinks(url, addr, port, timeout, extensions):

    url = url.encode('utf-8')
    addr = addr.encode('utf-8')
    port = str(port).encode('utf-8')

    go_linker.GetLinks(GoString(url, len(url)),
                       GoString(addr, len(addr)),
                       GoString(port, len(port)),
                       timeout,
                       extensions)
