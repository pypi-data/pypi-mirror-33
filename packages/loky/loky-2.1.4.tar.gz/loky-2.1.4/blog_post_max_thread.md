# A journey through cross platform management with `ctypes`


**The Goal**: dynamically set the number of threads used by scientific computing library, using `OpenMP`, `openBLAS` or `MKL`.

**The Why**:
When using a multiprocessing application, we often set the number of jobs to match the number of CPU. However, many scientific computing library like `numpy` relies on thread-pools for their operation that already use a number of threads equals to the number of CPU. When these libraries are used in the subprocesses, each process tries to use the maximal number of threads, resulting in a massive oversubscription: n_CPU * n_CPU instead of n_CPU. With this oversubscription, the multiprocessing program becomes slower than the original one. To mitigate this issue, one can set environment variable such as `OMP_NUM_THREADS=1` or `MKL_NUM_THREADS=1`.

In our effort to make parallel computing more accessible, we decided to implement an automatic mechanism to set the maximal number of thread dynamically in each process directly with `joblib`.

## Using environment variable to limit the number of threads in a subprocess

A first approach, using environment variable, is to use an initializer which set all the possible variable for these libraries to the desired number of threads. This behavior can easily be implemented using an initializer looking like:

```python
M_THREADED_COMPUTING_LIBRARIES_VARIABLES = [
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXP_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
]

def initializer(num_threads):
    if not isinstance(num_threads, int) or 

    import os
    for var in M_THREADED_COMPUTING_LIBRARY_VARIABLES:
        os.environ[var] = str(num_threads)
```

These different libraries cache this value once they have been started, causing two issues with this approach:

- The number of threads cannot be changed dynamically. this means that if the pool of process is resized, the number of threads cannot be adapted.
- Moreover, if the library is loaded in the process before the initializer, the given thread limit is not taken into account.

## Dynamic scaling of the number of threads in a subprocess

To cope with this issue, it is possible to directly interact with the considered library to set the maximal number of threads it can use. this approaches rely on `ctypes`, a module in the python standard library that allows the user to load and call function from C-libraries. First, it is necessary to find the location of the library file on the system considered.


### Looping through loaded library with `ctypes`

#### POSIX platforms

The recommended way to find a library on POSIX platform is to rely on `ctypes.util.find_library`. This utility looks up in the standard library folders -- *e.g.* `/usr/lib` or `/usr/local/lib` -- and find the most recent version of a given library. For instance, the proper way to localize the `libc` of a POSIX system would be to call `lib_path = find_library('c')`, which returns `'libc.so.6'` on my system. This path can latter be used to actually load the library, using `ctypes.CDLL(lib_path)`.

However, this method has two drawbacks. While this works for standard libraries installed via system package manager, the `find_library` function will fail for libraries installed in more exotic places, such as the libraries shipped by `conda`. For instance, this method fails to find the `libmkl` linked to the `numpy` module. Moreover, there is no way to determine wether a the library is already loaded or not.

To cope with that, we propose to loop through the library path of all loaded libraries. This can be done with the POSIX function [`dl_iterate_phdr`](https://linux.die.net/man/3/dl_iterate_phdr). This function is calling a callback function with arguments `info` of type `dl_phdr_info*`, `size` of type `size_t` and `data` of type `void*`. The `dl_phdr_info` structure can be mapped with a `ctypes` structure, using the information from the man-page of [`dl_iteration_phdr`](https://linux.die.net/man/3/dl_iterate_phdr), with

```python
UINT_ARCH = ctypes.c_uint64 if sys.maxsize > 2**32 else ctypes.c_uint32
class dl_phdr_info(ctypes.Structure):
    _fields_ = [("dlpi_addr",  UINT_ARCH),
                ("dlpi_name",  ctypes.c_char_p),
                ("dlpi_phdr",  ctypes.c_void_p),
                ("dlpi_phnum", ctypes.c_uint16)]
```

The type of the 2 last argument is irrelevant as we only care about the path of the library in `dlpi_name`.