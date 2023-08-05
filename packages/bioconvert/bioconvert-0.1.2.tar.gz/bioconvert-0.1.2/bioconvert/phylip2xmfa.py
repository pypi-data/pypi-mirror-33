# -*- coding: utf-8 -*-
#
#  This file is part of Bioconvert software
#
#  Copyright (c) 2017 - Bioconvert Development Team
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/biokit/bioconvert
#  documentation: http://bioconvert.readthedocs.io
#
##############################################################################
"""PHYLIP2XMFA conversion"""
import os

import colorlog
from Bio import SeqIO

from bioconvert import ConvBase
from bioconvert.core.decorators import requires

_log = colorlog.getLogger(__name__)


__all__ = ['PHYLIP2XMFA']


class PHYLIP2XMFA(ConvBase):
    """
    Converts a sequence alignment from :term:`PHYLIP` format to :term:`XMFA` format. ::
    """
    _default_method = 'biopython'

    def __init__(self, infile, outfile=None, *args, **kwargs):
        """.. rubric:: constructor

        :param str infile: input :term:`PHYLIP` file.
        :param str outfile: (optional) output :term:`NEXUS` file
        """
        super().__init__(infile, outfile)
        self.alphabet = None

    @requires(python_libraries=["biopython"])
    def _method_biopython(self, *args, **kwargs):
        """
        Convert :term:`PHYLIP` interleaved file in :term:`XMFA` (Mauve)format.

        """
        sequences = list(SeqIO.parse(self.infile, "phylip", alphabet=self.alphabet))
        count = SeqIO.write(sequences, self.outfile, "mauve")
        _log.info("Converted %d records to phylip" % count)


