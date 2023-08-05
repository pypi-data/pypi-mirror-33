"""
GPU driver for C kernels

There should be a single GPU environment running on the system.  This
environment is constructed on the first call to :func:`env`, and the
same environment is returned on each call.

After retrieving the environment, the next step is to create the kernel.
This is done with a call to :meth:`GpuEnvironment.make_kernel`, which
returns the type of data used by the kernel.

Next a :class:`GpuData` object should be created with the correct kind
of data.  This data object can be used by multiple kernels, for example,
if the target model is a weighted sum of multiple kernels.  The data
should include any extra evaluation points required to compute the proper
data smearing.  This need not match the square grid for 2D data if there
is an index saying which q points are active.

Together the GpuData, the program, and a device form a :class:`GpuKernel`.
This kernel is used during fitting, receiving new sets of parameters and
evaluating them.  The output value is stored in an output buffer on the
devices, where it can be combined with other structure factors and form
factors and have instrumental resolution effects applied.

In order to use OpenCL for your models, you will need OpenCL drivers for
your machine.  These should be available from your graphics card vendor.
Intel provides OpenCL drivers for CPUs as well as their integrated HD
graphics chipsets.  AMD also provides drivers for Intel CPUs, but as of
this writing the performance is lacking compared to the Intel drivers.
NVidia combines drivers for CUDA and OpenCL in one package.  The result
is a bit messy if you have multiple drivers installed.  You can see which
drivers are available by starting python and running:

    import pyopencl as cl
    cl.create_some_context(interactive=True)

Once you have done that, it will show the available drivers which you
can select.  It will then tell you that you can use these drivers
automatically by setting the SAS_OPENCL environment variable, which is
PYOPENCL_CTX equivalent but not conflicting with other pyopnecl programs.

Some graphics cards have multiple devices on the same card.  You cannot
yet use both of them concurrently to evaluate models, but you can run
the program twice using a different device for each session.

OpenCL kernels are compiled when needed by the device driver.  Some
drivers produce compiler output even when there is no error.  You
can see the output by setting PYOPENCL_COMPILER_OUTPUT=1.  It should be
harmless, albeit annoying.
"""
from __future__ import print_function

import os
import warnings
import logging
import time

import numpy as np  # type: ignore


# Attempt to setup opencl. This may fail if the opencl package is not
# installed or if it is installed but there are no devices available.
try:
    import pycuda.autoinit
    import pycuda.driver as cuda  # type: ignore
    from pycuda.compiler import SourceModule
    HAVE_CUDA = True
    CUDA_ERROR = ""
except Exception as exc:
    HAVE_CUDA = False
    CUDA_ERROR = str(exc)

from . import generate
from .kernel import KernelModel, Kernel

# pylint: disable=unused-import
try:
    from typing import Tuple, Callable, Any
    from .modelinfo import ModelInfo
    from .details import CallDetails
except ImportError:
    pass
# pylint: enable=unused-import

# The max loops number is limited by the amount of local memory available
# on the device.  You don't want to make this value too big because it will
# waste resources, nor too small because it may interfere with users trying
# to do their polydispersity calculations.  A value of 1024 should be much
# larger than necessary given that cost grows as npts^k where k is the number
# of polydisperse parameters.
MAX_LOOPS = 2048


# Pragmas for enable OpenCL features.  Be sure to protect them so that they
# still compile even if OpenCL is not present.
_F16_PRAGMA = """\
#if defined(__OPENCL_VERSION__) // && !defined(cl_khr_fp16)
#  pragma OPENCL EXTENSION cl_khr_fp16: enable
#endif
"""

_F64_PRAGMA = """\
#if defined(__OPENCL_VERSION__) // && !defined(cl_khr_fp64)
#  pragma OPENCL EXTENSION cl_khr_fp64: enable
#endif
"""

def use_cuda():
    return HAVE_CUDA

ENV = None
def reset_environment():
    """
    Call to create a new OpenCL context, such as after a change to SAS_OPENCL.
    """
    global ENV
    ENV = GpuEnvironment() if use_cuda() else None

def environment():
    # type: () -> "GpuEnvironment"
    """
    Returns a singleton :class:`GpuEnvironment`.

    This provides an OpenCL context and one queue per device.
    """
    if ENV is None:
        if not HAVE_CUDA:
            raise RuntimeError("OpenCL startup failed with ***"
                               + CUDA_ERROR + "***; using C compiler instead")
        reset_environment()
        if ENV is None:
            raise RuntimeError("SAS_OPENCL=None in environment")
    return ENV

def has_type(device, dtype):
    # type: (cl.Device, np.dtype) -> bool
    """
    Return true if device supports the requested precision.
    """
    if dtype == generate.F32:
        return True
    elif dtype == generate.F64:
        return "cl_khr_fp64" in device.extensions
    elif dtype == generate.F16:
        return "cl_khr_fp16" in device.extensions
    else:
        return False

def _stretch_input(vector, dtype, extra=1e-3, boundary=32):
    # type: (np.ndarray, np.dtype, float, int) -> np.ndarray
    """
    Stretch an input vector to the correct boundary.

    Performance on the kernels can drop by a factor of two or more if the
    number of values to compute does not fall on a nice power of two
    boundary.   The trailing additional vector elements are given a
    value of *extra*, and so f(*extra*) will be computed for each of
    them.  The returned array will thus be a subset of the computed array.

    *boundary* should be a power of 2 which is at least 32 for good
    performance on current platforms (as of Jan 2015).  It should
    probably be the max of get_warp(kernel,queue) and
    device.min_data_type_align_size//4.
    """
    remainder = vector.size % boundary
    if remainder != 0:
        size = vector.size + (boundary - remainder)
        vector = np.hstack((vector, [extra] * (size - vector.size)))
    return np.ascontiguousarray(vector, dtype=dtype)


def compile_model(context, source, dtype, fast=False):
    # type: (cl.Context, str, np.dtype, bool) -> cl.Program
    """
    Build a model to run on the gpu.

    Returns the compiled program and its type.  The returned type will
    be float32 even if the desired type is float64 if any of the
    devices in the context do not support the cl_khr_fp64 extension.
    """
    dtype = np.dtype(dtype)
    if not all(has_type(d, dtype) for d in context.devices):
        raise RuntimeError("%s not supported for devices"%dtype)

    source_list = [generate.convert_type(source, dtype)]

    if dtype == generate.F16:
        source_list.insert(0, _F16_PRAGMA)
    elif dtype == generate.F64:
        source_list.insert(0, _F64_PRAGMA)

    source_list.insert(0, "#define USE_SINCOS\n")
    source = "\n".join(source_list)
    program = SourceModule(source, no_extern_c=True) # include_dirs=[...]
    #print("done with "+program)
    return program


# for now, this returns one device in the context
# TODO: create a context that contains all devices on all platforms
class GpuEnvironment(object):
    """
    GPU context, with possibly many devices, and one queue per device.
    """
    def __init__(self, devnum=0):
        # type: () -> None
        # Byte boundary for data alignment
        #self.data_boundary = max(d.min_data_type_align_size
        #                         for d in self.context.devices)
        self.compiled = {}
        #self.device = cuda.Device(devnum)
        #self.context = self.device.make_context()

    def has_type(self, dtype):
        # type: (np.dtype) -> bool
        """
        Return True if all devices support a given type.
        """
        return True

    def compile_program(self, name, source, dtype, fast, timestamp):
        # type: (str, str, np.dtype, bool, float) -> cl.Program
        """
        Compile the program for the device in the given context.
        """
        # Note: PyOpenCL caches based on md5 hash of source, options and device
        # so we don't really need to cache things for ourselves.  I'll do so
        # anyway just to save some data munging time.
        tag = generate.tag_source(source)
        key = "%s-%s-%s%s"%(name, dtype, tag, ("-fast" if fast else ""))
        # Check timestamp on program
        program, program_timestamp = self.compiled.get(key, (None, np.inf))
        if program_timestamp < timestamp:
            del self.compiled[key]
        if key not in self.compiled:
            logging.info("building %s for CUDA", key)
            program = compile_model(str(source), dtype, fast)
            self.compiled[key] = (program, timestamp)
        return program

class GpuModel(KernelModel):
    """
    GPU wrapper for a single model.

    *source* and *model_info* are the model source and interface as returned
    from :func:`generate.make_source` and :func:`generate.make_model_info`.

    *dtype* is the desired model precision.  Any numpy dtype for single
    or double precision floats will do, such as 'f', 'float32' or 'single'
    for single and 'd', 'float64' or 'double' for double.  Double precision
    is an optional extension which may not be available on all devices.
    Half precision ('float16','half') may be available on some devices.
    Fast precision ('fast') is a loose version of single precision, indicating
    that the compiler is allowed to take shortcuts.
    """
    def __init__(self, source, model_info, dtype=generate.F32, fast=False):
        # type: (Dict[str,str], ModelInfo, np.dtype, bool) -> None
        self.info = model_info
        self.source = source
        self.dtype = dtype
        self.fast = fast
        self.program = None # delay program creation
        self._kernels = None

    def __getstate__(self):
        # type: () -> Tuple[ModelInfo, str, np.dtype, bool]
        return self.info, self.source, self.dtype, self.fast

    def __setstate__(self, state):
        # type: (Tuple[ModelInfo, str, np.dtype, bool]) -> None
        self.info, self.source, self.dtype, self.fast = state
        self.program = None

    def make_kernel(self, q_vectors):
        # type: (List[np.ndarray]) -> "GpuKernel"
        if self.program is None:
            compile_program = environment().compile_program
            timestamp = generate.ocl_timestamp(self.info)
            self.program = compile_program(
                self.info.name,
                self.source['opencl'],
                self.dtype,
                self.fast,
                timestamp)
            variants = ['Iq', 'Iqxy', 'Imagnetic']
            names = [generate.kernel_name(self.info, k) for k in variants]
            kernels = [getattr(self.program, k) for k in names]
            self._kernels = dict((k, v) for k, v in zip(variants, kernels))
        is_2d = len(q_vectors) == 2
        if is_2d:
            kernel = [self._kernels['Iqxy'], self._kernels['Imagnetic']]
        else:
            kernel = [self._kernels['Iq']]*2
        return GpuKernel(kernel, self.dtype, self.info, q_vectors)

    def release(self):
        # type: () -> None
        """
        Free the resources associated with the model.
        """
        if self.program is not None:
            self.program = None

    def __del__(self):
        # type: () -> None
        self.release()

# TODO: check that we don't need a destructor for buffers which go out of scope
class GpuInput(object):
    """
    Make q data available to the gpu.

    *q_vectors* is a list of q vectors, which will be *[q]* for 1-D data,
    and *[qx, qy]* for 2-D data.  Internally, the vectors will be reallocated
    to get the best performance on OpenCL, which may involve shifting and
    stretching the array to better match the memory architecture.  Additional
    points will be evaluated with *q=1e-3*.

    *dtype* is the data type for the q vectors. The data type should be
    set to match that of the kernel, which is an attribute of
    :class:`GpuProgram`.  Note that not all kernels support double
    precision, so even if the program was created for double precision,
    the *GpuProgram.dtype* may be single precision.

    Call :meth:`release` when complete.  Even if not called directly, the
    buffer will be released when the data object is freed.
    """
    def __init__(self, q_vectors, dtype=generate.F32):
        # type: (List[np.ndarray], np.dtype) -> None
        # TODO: do we ever need double precision q?
        self.nq = q_vectors[0].size
        self.dtype = np.dtype(dtype)
        self.is_2d = (len(q_vectors) == 2)
        # TODO: stretch input based on get_warp()
        # not doing it now since warp depends on kernel, which is not known
        # at this point, so instead using 32, which is good on the set of
        # architectures tested so far.
        if self.is_2d:
            # Note: 16 rather than 15 because result is 1 longer than input.
            width = ((self.nq+16)//16)*16
            self.q = np.empty((width, 2), dtype=dtype)
            self.q[:self.nq, 0] = q_vectors[0]
            self.q[:self.nq, 1] = q_vectors[1]
        else:
            # Note: 32 rather than 31 because result is 1 longer than input.
            width = ((self.nq+32)//32)*32
            self.q = np.empty(width, dtype=dtype)
            self.q[:self.nq] = q_vectors[0]
        self.global_size = [self.q.shape[0]]
        #print("creating inputs of size", self.global_size)
        self.q_b = cuda.to_device(self.q)

    def release(self):
        # type: () -> None
        """
        Free the memory.
        """
        if self.q_b is not None:
            self.q_b.free()
            self.q_b = None

    def __del__(self):
        # type: () -> None
        self.release()

class GpuKernel(Kernel):
    """
    Callable SAS kernel.

    *kernel* is the GpuKernel object to call

    *model_info* is the module information

    *q_vectors* is the q vectors at which the kernel should be evaluated

    *dtype* is the kernel precision

    The resulting call method takes the *pars*, a list of values for
    the fixed parameters to the kernel, and *pd_pars*, a list of (value,weight)
    vectors for the polydisperse parameters.  *cutoff* determines the
    integration limits: any points with combined weight less than *cutoff*
    will not be calculated.

    Call :meth:`release` when done with the kernel instance.
    """
    def __init__(self, kernel, dtype, model_info, q_vectors):
        # type: (cl.Kernel, np.dtype, ModelInfo, List[np.ndarray]) -> None
        q_input = GpuInput(q_vectors, dtype)
        self.kernel = kernel
        self.info = model_info
        self.dtype = dtype
        self.dim = '2d' if q_input.is_2d else '1d'
        # plus three for the normalization values
        self.result = np.empty(q_input.nq+1, dtype)

        # Inputs and outputs for each kernel call
        # Note: res may be shorter than res_b if global_size != nq
        self.result_b = cuda.mem_alloc(q_input.global_size[0] * dtype.itemsize)
        self.q_input = q_input # allocated by GpuInput above

        self._need_release = [self.result_b, self.q_input]
        self.real = (np.float32 if dtype == generate.F32
                     else np.float64 if dtype == generate.F64
                     else np.float16 if dtype == generate.F16
                     else np.float32)  # will never get here, so use np.float32

    def __call__(self, call_details, values, cutoff, magnetic):
        # type: (CallDetails, np.ndarray, np.ndarray, float, bool) -> np.ndarray
        # Arrange data transfer to card
        details_b = cuda.to_device(call_details.buffer)
        values_b = cuda.to_device(values)

        kernel = self.kernel[1 if magnetic else 0]
        args = [
            np.uint32(self.q_input.nq), None, None,
            details_b, values_b, self.q_input.q_b, self.result_b,
            self.real(cutoff),
        ]
        grid = partition(self.q_input.nq)
        #print("Calling OpenCL")
        #call_details.show(values)
        # Call kernel and retrieve results
        last_nap = time.clock()
        step = 1000000//self.q_input.nq + 1
        for start in range(0, call_details.num_eval, step):
            stop = min(start + step, call_details.num_eval)
            #print("queuing",start,stop)
            args[1:3] = [np.int32(start), np.int32(stop)]
            kernel(*args, **grid)
            if stop < call_details.num_eval:
                sync()
                # Allow other processes to run
                current_time = time.clock()
                if current_time - last_nap > 0.5:
                    time.sleep(0.05)
                    last_nap = current_time
        sync()
        self.details_b.free()
        self.values_b.free()
        cuda.memcpy_dtoh(self.result, self.result_b)
        #print("result", self.result)

        pd_norm = self.result[self.q_input.nq]
        scale = values[0]/(pd_norm if pd_norm != 0.0 else 1.0)
        background = values[1]
        #print("scale",scale,values[0],self.result[self.q_input.nq],background)
        return scale*self.result[:self.q_input.nq] + background
        # return self.result[:self.q_input.nq]

    def release(self):
        # type: () -> None
        """
        Release resources associated with the kernel.
        """
        if self.result_b is not None:
            self.result_b.free()
            self.result_b = None

    def __del__(self):
        # type: () -> None
        self.release()


def sync():
    """
    Overview:
        Waits for operation in the current context to complete.

    Note: Maybe context.synchronize() is sufficient.
    """
    #return # The following works in C++; don't know what pycuda is doing
    # Create an event with which to synchronize
    done = cuda.Event()

    # Schedule an event trigger on the GPU.
    done.record()

    #line added to not hog resources
    while not done.query(): time.sleep(0.01)

    # Block until the GPU executes the kernel.
    done.synchronize()
    # Clean up the event; I don't think they can be reused.
    del done


def partition(n):
    '''
    Overview:
        Auto grids the thread blocks to achieve some level of calculation
    efficiency.
    '''
    max_gx, max_gy = 65535, 65535
    blocksize = 32
    #max_gx, max_gy = 5, 65536
    #blocksize = 3
    block = (blocksize, 1, 1)
    num_blocks = int((n+blocksize-1)/blocksize)
    if num_blocks < max_gx:
        grid = (num_blocks, 1)
    else:
        gx = max_gx
        gy = (num_blocks + max_gx - 1) / max_gx
        if gy >= max_gy:
            raise ValueError("vector is too large")
        grid = (gx, gy)
    #print("block", block, "grid", grid)
    #print("waste", block[0]*block[1]*block[2]*grid[0]*grid[1] - n)
    return dict(block=block, grid=grid)
