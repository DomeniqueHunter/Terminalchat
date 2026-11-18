import ctypes
import ctypes.util
import gc


_libc = None


def load_libc() -> ctypes.CDLL | None:
    global _libc
    if _libc is None:
        name = ctypes.util.find_library("c")
        try:
            _libc = ctypes.CDLL(name) if name else False
        except OSError:
            _libc = False
    return _libc or None


def trim_memory() -> bool:
    gc.collect()
    libc = load_libc()
    if libc is None or not hasattr(libc, "malloc_trim"):
        return False
    return bool(libc.malloc_trim(0))


def main() -> None:
    print("trimmed:", trim_memory())


if __name__ == "__main__":
    main()
