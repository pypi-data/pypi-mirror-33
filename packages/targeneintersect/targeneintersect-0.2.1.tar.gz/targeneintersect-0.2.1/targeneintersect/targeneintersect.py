# -*- coding: utf-8 -*-

"""Main module."""

import pybedtools


def target_gene_intersect(genes, dataframe):
    """Uses pybedtools intersect to find target genes for dataframe"""
    gene_frame = pybedtools.BedTool(genes)
    cols_ = dataframe.shape[1]
    keep = list(range(6, 6+cols_))
    keep.insert(0, 3)
    intersect = gene_frame.intersect(pybedtools.BedTool.from_dataframe(
       dataframe), wb=True).saveas().to_dataframe().iloc[:, keep]
    return intersect
