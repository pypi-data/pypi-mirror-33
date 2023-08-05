"""Convert :term:`BAM` format to :term:`JSON` file"""
from bioconvert import ConvBase

import colorlog

from bioconvert.core.decorators import requires

logger = colorlog.getLogger(__name__)



class BAM2JSON(ConvBase):
    """Bam2Json converter

    Convert bam file to json file.
    """
    _default_method = "bamtools"

    def __init__(self, infile, outfile):
        """.. rubric:: constructor
        :param str infile:
        :param str outfile:
        """
        super().__init__(infile, outfile)

    @requires("bamtools")
    def _method_bamtools(self, *args, **kwargs):
        """
        do the conversion :term`BAM` -> :term:'JSON` using bamtools

        """

        cmd = "bamtools convert -format json -in {0} -out {1}".format(
            self.infile, self.outfile
        )
        self.execute(cmd)
