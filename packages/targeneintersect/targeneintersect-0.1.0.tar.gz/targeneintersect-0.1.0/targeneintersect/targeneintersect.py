# -*- coding: utf-8 -*-

"""Main module."""

import pandas as pd
import pybedtools

def target_gene_intersect(genes, dataframe):
    """ Use pybedtools intersect to get target genes for some bed formatted dataframe of Drosophila melanogaster data"""
    gene_frame = pybedtools.BedTool(genes)
    cols_ = dataframe.shape[1]
    keep = list(range(6, 6+cols_))
    keep.insert(0, 3)
    intersect = gene_frame.intersect(pybedtools.BedTool.from_dataframe(dataframe), 
            wb=True).saveas().to_dataframe().iloc[:, keep] 
    return intersect
 
