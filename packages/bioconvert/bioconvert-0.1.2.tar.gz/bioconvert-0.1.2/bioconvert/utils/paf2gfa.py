#https://gitlab.inria.fr/pmarijon/paf2gfa/blob/master/paf2gfa/parser.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from enum import Enum
from types import SimpleNamespace
from collections import defaultdict

import networkx as nx

class ParsingWarning(Enum):

    NOTHING = ""
    LINK_REPLACE_LENGTH = "Replace previous overlap between same read with less overlap length"
    LINK_REPLACE_MATCH = "Replace previous overlap between same read with less kmer match"
    LINK_REPLACE_OVMAPLEN = "Replace previous overlap between same read with higher overhang map length ratio"
    CONTAINMENT_PREVIOUS = "We see a containment A in B previously"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class Parser:

    def __init__(self, containment=True, internal=True,
                 internal_match_threshold=0.8):
        self.__cores = ["read_a", "len_a", "beg_a", "end_a", "strand",
                        "read_b", "len_b", "beg_b", "end_b",
                        "nb_match", "nb_base", "qual"]
        self.__containment = containment
        self.__internal = internal

        self.__graph = nx.DiGraph()
        self.__containments = defaultdict(list)

        self.__overhang_maplen_ratio_limit = internal_match_threshold

    @property
    def containment(self):
        return self.__containment

    @containment.setter
    def containment(self, value):
        self.__containment = value

    @containment.getter
    def containment(self):
        return self.__containment

    @property
    def internal(self):
        return self.__internal

    @internal.setter
    def internal(self, value):
        self.__internal = value

    @internal.getter
    def internal(self):
        return self.__internal

    @property
    def graph(self):
        return self.__graph

    def parse_line(self, line):
        """
        Parse PAF line

        Return None, or a ParsingWarning object
        """

        l = SimpleNamespace(
            **{self.__cores[i]: v for i, v in enumerate(re.split(r"\s+",line)[:12])})

        l = Parser.__line_type_correction(l)

        if l.read_a == l.read_b:
            return

        self._add_segment(l.read_a, l.len_a)
        self._add_segment(l.read_b, l.len_b)

        overhang = Parser.__compute_overhang(l)
        maplen = max(l.end_a - l.beg_a, l.end_b - l.beg_b)

        if overhang > maplen*self.__overhang_maplen_ratio_limit or overhang > 1000:
            # Strange overlap

            if l.strand == "+":
                return self._add_internal(l.read_a, "+", l.read_b, "+",
                                          l.nb_base, l.nb_match,
                                          overhang/maplen)
            return self._add_internal(l.read_a, "+", l.read_b, "-", l.nb_base,
                                      l.nb_match, overhang/maplen)

        elif l.strand == "+" and l.beg_a <= l.beg_b and l.len_a - l.end_a < l.len_b - l.end_b:
            # B containe A
            return self._add_containment(l.read_b, "+", l.read_a, "+", l.beg_b,
                                         l.nb_base, l.len_b, l.len_a)
        elif l.strand == "-" and l.beg_a <= l.len_b - l.end_b and l.len_a - l.end_a < l.beg_b:
            # B containe A
            return self._add_containment(l.read_b, "+", l.read_a, "-", l.beg_b,
                                         l.nb_base, l.len_b, l.len_a)
        elif l.strand == "+" and l.beg_a >= l.beg_b and l.len_a - l.end_a > l.len_b - l.end_b:
            # A containe B
            return self._add_containment(l.read_a, "+", l.read_b, "+", l.beg_a,
                                         l.nb_base, l.len_a, l.len_b)
        elif l.strand == "-" and l.beg_a >= l.len_b - l.end_b and l.len_a - l.end_a > l.beg_b:
            # A containe B
            return self._add_containment(l.read_a, "+", l.read_b, "-", l.beg_a,
                                         l.nb_base, l.len_a, l.len_b)
        elif l.strand == "+":
            if l.beg_a > l.beg_b:
                # A overlap B
                return self._add_link(l.read_a, "+", l.read_b, "+", l.nb_base,
                                      l.nb_match, overhang/maplen)

            # B overlap A
            return self._add_link(l.read_b, "+", l.read_a, "+", l.nb_base,
                                  l.nb_match, overhang/maplen)
        else:
            if l.beg_a > l.len_a - l.end_a:
                if l.beg_a > l.len_b - l.end_b:
                    return self._add_link(l.read_a, "+", l.read_b, "-",
                                          l.nb_base, l.nb_match,
                                          overhang/maplen)
                return self._add_link(l.read_b, "+", l.read_a, "-", l.nb_base,
                                      l.nb_match, overhang/maplen)
            else:
                if l.len_a - l.beg_a > l.end_b:
                    return self._add_link(l.read_a, "-", l.read_b, "+",
                                          l.nb_base, l.nb_match,
                                          overhang/maplen)
                return self._add_link(l.read_b, "-", l.read_a, "+", l.nb_base,
                                      l.nb_match, overhang/maplen)

    def parse_lines(self, lines):
        for line in lines:
            if line.strip() != "":
                self.parse_line(line)

    def generate_gfa(self):
        yield "H\tVN:Z:1.0"
        remove_node = set()

        if not self.__containment:
            for contained in self.__containments:
                remove_node.add(contained)

            self.__containments = defaultdict(list)
            for c in remove_node:
                self.__graph.remove_node(c)

        remove_node = set()

        for c in nx.weakly_connected_components(self.__graph):
            if len(c) == 1:
                remove_node.add(*c)

        for c in remove_node:
            self.__graph.remove_node(c)

        if self.__containment:
            for contained, list_container in self.__containments.items():
                for container, *_, len_ner, len_ned in list_container:
                    self.__graph.add_node(contained, length=len_ned)
                    self.__graph.add_node(container, length=len_ner)

        for n, data in self.__graph.nodes(data=True):
            yield "S\t{}\t*\tLN:i:{}".format(n, data["length"])

        for (u, v, data) in self.__graph.edges(data=True):
            yield "L\t{}\t{}\t{}\t{}\t{}M\tNM:i:{}\tom:f:{:.2f}".format(
                u, data["strand_a"], v, data["strand_b"], data["ov_len"],
                int(data["ov_len"]) - int(data["nb_match"]),
                data["overhang_maplen"])

        for conted, list_conter in self.__containments.items():
            for (conter, straner, straned, pos, ov, *_) in list_conter:
                yield "\t".join(["C", conter, straner, conted, straned,
                                 str(pos), str(ov)]) + "M"

    def get_gfa(self):
        return "\n".join(list(self.generate_gfa()))

    def _add_segment(self, name, length):
        self.__graph.add_node(name, length=length)

    def _add_link(self, name_a, strand_a, name_b, strand_b, ov_len, nb_match,
                  overhang_maplen):
        """
        Add link between two read
        - name_a: read A name
        - strand_a: read A strand
        - name_b: read B name
        - strand_b: read B strand
        - ov_len: length of overlap
        - nb_match: nomber of kmer match
        - overhang_maplen: overhang map length ratio

        Return None if all its ok or ParsingWarning
        """
        if self.__graph.has_edge(name_a, name_b):
            edge = self.__graph[name_a][name_b]
            if edge["ov_len"] < ov_len:
                self.__graph.remove_edge(name_a, name_b)
                self.__graph.add_edge(name_a, name_b, strand_a=strand_a,
                                      strand_b=strand_b, ov_len=ov_len,
                                      nb_match=nb_match,
                                      overhang_maplen=overhang_maplen)
                return ParsingWarning.LINK_REPLACE_LENGTH

            elif edge["nb_match"] < nb_match:
                self.__graph.remove_edge(name_a, name_b)
                self.__graph.add_edge(name_a, name_b, strand_a=strand_a,
                                      strand_b=strand_b, ov_len=ov_len,
                                      nb_match=nb_match,
                                      overhang_maplen=overhang_maplen)
                return ParsingWarning.LINK_REPLACE_MATCH

            elif edge["overhang_maplen"] > overhang_maplen:
                self.__graph.remove_edge(name_a, name_b)
                self.__graph.add_edge(name_a, name_b, strand_a=strand_a,
                                      strand_b=strand_b, ov_len=ov_len,
                                      nb_match=nb_match,
                                      overhang_maplen=overhang_maplen)
                return ParsingWarning.LINK_REPLACE_OVMAPLEN
        else:
            self.__graph.add_edge(name_a, name_b, strand_a=strand_a, strand_b=strand_b,
                                  ov_len=ov_len, nb_match=nb_match,
                                  overhang_maplen=overhang_maplen)
            return None

    def _add_internal(self, name_a, strand_a, name_b, strand_b, ov_len,
                      nb_match, overhang_maplen):
        """
        If internal match are keep, add this link a link
        - name_a: read A name
        - strand_a: read A strand
        - name_b: read B name
        - strand_b: read B strand
        - ov_len: length of overlap
        - nb_match: nomber of kmer match
        - overhang_maplen: overhang map length ratio

        Return None if all its ok or a string with warning message
        """
        if self.__internal:
            return self._add_link(name_a, strand_a, name_b, strand_b, ov_len,
                                  nb_match, overhang_maplen)

        return None

    def _add_containment(self, container, strand_ner, contained, strand_ned,
                         pos, length, len_ner, len_ned):
        """
        Add containment in __containments dict
        - container: container read name
        - strand_ner: strand container read
        - contained: contained read name
        - strand_ned: strand contained read
        - pos: position of containment begin
        - length: length of overlap
        - len_ner: length of container
        - len_ned: length of contained

        Return None if all its ok or a string with warning message
        """

        self.__containments[contained].append((container, strand_ner,
                                               strand_ned, pos, length,
                                               len_ner, len_ned))

        if container in self.__containments and \
        any([contained == c[0] for c in self.__containments[container]]):
            return ParsingWarning.CONTAINMENT_PREVIOUS
        return None

    @staticmethod
    def __line_type_correction(l):
        l.beg_a = int(l.beg_a)
        l.end_a = int(l.end_a)
        l.len_a = int(l.len_a)

        l.beg_b = int(l.beg_b)
        l.end_b = int(l.end_b)
        l.len_b = int(l.len_b)

        return l

    @staticmethod
    def __compute_overhang(l):
        if l.strand == "+":
            return min(l.beg_a, l.beg_b) + min(l.len_a - l.end_a, l.len_b -
l.end_b)
        return min(l.beg_a, l.len_b - l.end_b) + min(l.beg_b, l.len_a - l.end_a)


