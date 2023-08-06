import sys

class SVGParserError(Exception):
    pass


VALID_DPI_UNITS = ('px', 'pt', 'pc', 'mm', 'cm', 'in')

def _dpi_conv(dpi: str):
    if dpi[-2:] not in VALID_DPI_UNITS:
        raise ValueError("dpi needs to be one of {}, got {}".format(VALID_DPI_UNITS, dpi[-2:]))
    units = dpi[-2:].encode('UTF-8')
    _dpi = float(dpi[:-2])
    return units, _dpi


cdef class Parser:
    """
    Cython class for parsing SVG files.
    """

    @staticmethod
    def parse(svg, dpi: str = '96px') -> SVG:
        """
        Creates an SVG image from an SVG string. Units for dpi are 'px', 'pt',
        'pc' 'mm', 'cm', or 'in'.
        """
        units, magnitude = _dpi_conv(dpi)
        im = SVG()
        if isinstance(svg, str):
            s = svg.encode('UTF-8')
        elif isinstance(svg, bytes):
            s = svg
        else:
            raise TypeError("svg must be either str or bytes, found {}".format(type(svg)))
        im._nsvgimage = nsvgParse(s, units, magnitude)
        if im._nsvgimage == NULL:
            raise SVGParserError("Could not parse SVG from string.")
        else:
            return im

    @staticmethod
    def parse_file(filename: str, dpi: str = '96px') -> SVG:
        """
        Creates an SVG image from filename. Units for dpi are 'px', 'pt',
        'pc' 'mm', 'cm', or 'in'.
        """
        file = filename.encode(sys.getfilesystemencoding())
        units, magnitude = _dpi_conv(dpi)
        im = SVG()
        im._nsvgimage = nsvgParseFromFile(file, units, magnitude)
        if im._nsvgimage == NULL:
            raise SVGParserError(
                "Could not parse SVG from {}".format(file)
                )
        else:
            return im
