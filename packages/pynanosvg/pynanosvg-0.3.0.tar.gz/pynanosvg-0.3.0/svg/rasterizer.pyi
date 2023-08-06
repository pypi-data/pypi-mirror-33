import cython

class SVGRasterizerError(Exception):
    pass


cdef class Rasterizer:
    """Cython class parsing and rendering SVG images."""
    cdef NSVGrasterizer* _nsvgrasterizer

    def __cinit__(self):
        self._nsvgrasterizer = nsvgCreateRasterizer()

    def __dealloc__(self):
        if self._nsvgrasterizer != NULL:
            nsvgDeleteRasterizer(self._nsvgrasterizer)

    def rasterize(self, svg: SVG,
                  width: cython.int,
                  height: cython.int,
                  scale: cython.float = 1.0,
                  tx: cython.int = 0,
                  ty: cython.int = 0) -> bytes:
        """
        Rasterizes the SVG into a new buffer of bytes forming an RGBA image.
        """
        if svg._nsvgimage == NULL:
            raise ValueError('The given SVG is empty, you must parse the SVG first.')
        # used to calculate size of buffer
        length = width * height * 4
        stride = width * 4
        buff = bytes(length)
        nsvgRasterize(self._nsvgrasterizer,
                      svg._nsvgimage, tx, ty, scale,
                      buff, width, height, stride)
        return buff

    def rasterize_to_buffer(self, svg: SVG,
                            width: cython.int,
                            height: cython.int,
                            stride: cython.int,
                            buffer: bytes,
                            scale: cython.float = 1.0,
                            tx: cython.int = 0,
                            ty: cython.int = 0,
                            ):
        """
        Rasterizes the SVG into a given buffer, which should be of length width * height * 4. Stride is usually width * 4.
        """
        if not isinstance(buffer, bytes):
            raise TypeError("`buffer` must be bytes, found {}".format(type(buffer)))
        if stride <= 0:
            raise ValueError('You must set a stride to rasterize to a buffer, stride must be positive.')
        if svg._nsvgimage == NULL:
            raise ValueError('The given SVG is empty, you must parse the SVG first.')
        nsvgRasterize(self._nsvgrasterizer,
                      svg._nsvgimage, tx, ty, scale,
                      buffer, width, height, stride)
        return buffer
