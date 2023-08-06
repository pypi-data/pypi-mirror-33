#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `targeneintersect` package."""

import pytest
import pandas as pd

from targeneintersect import targeneintersect


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    import requests
    return requests.get('https://github.com/isabelleberger/targeneintersect')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    from bs4 import BeautifulSoup
    assert 'GitHub' in BeautifulSoup(response.content).title.string

def test_target_gene_intersect(capsys):
    #Read in example data
    genes = 'tests/data/dmel6.12.genes.bed'
    motif_data = pd.read_table('tests/data/example_motif_data.bed', header=None)
    #Test function
    test_run = targeneintersect.target_gene_intersect(genes, motif_data) 
    #Make sure output is correct
    correct_out = pd.read_table('tests/data/correct_output')
    assert test_run.equals(correct_out)
