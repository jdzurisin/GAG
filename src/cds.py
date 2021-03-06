#!/usr/bin/env python

import copy
from src.gene_part import *

class CDS(GenePart):

    def __init__(self, identifier=None, indices=None, \
                 score=None, phase=None, strand=None, parent_id=None):
        GenePart.__init__(self, feature_type='CDS', identifier=identifier, \
                indices=indices, score=score, strand=strand, parent_id=parent_id)
        self.phase = []
        if phase is not None:
            self.phase.append(phase)

    def get_phase(self, i):
        """Returns phase for given segment of CDS."""
        if self.phase and len(self.phase) > i:
            return self.phase[i]
        else:
            return "."

    def add_phase(self, ph):
        """Appends phase to CDS"""
        self.phase.append(ph)

    def get_start_indices(self, strand):
        """Returns coordinates of first and third base of CDS."""
        if strand == '+':
            first_index = self.indices[0][0]
            return [first_index, first_index+2]
        elif strand == '-':
            first_index = self.indices[0][1]
            return [first_index-2, first_index]

    def get_stop_indices(self, strand):
        """Returns coordinates of third-to-last and last base of CDS."""
        if strand == '+':
            last_index_pair = self.indices[len(self.indices)-1]
            last_index = last_index_pair[1]
            return [last_index-2, last_index]
        elif strand == '-':
            last_index_pair = self.indices[len(self.indices)-1]
            last_index = last_index_pair[0]
            return [last_index, last_index+2]

    def extract_sequence(self, seq_object, strand):
        """Returns nucleotide sequence corresponding to CDS.

        Args:
            seq_object: the actual Sequence containing the CDS. I know, I know.
            strand: either '+' or '-'
        Returns:
            a string of nucleotides (or an empty string if strand is invalid or 
            CDS has no indices)
        """
        seq = ''
        for i in xrange(len(self.indices)):
            index_pair = self.indices[i]
            subseq = seq_object.get_subseq(index_pair[0], index_pair[1])
            if subseq:
                seq += subseq
        if strand == '-':
            seq = translate.reverse_complement(seq)
        return seq

    def to_tbl(self, has_start, has_stop):
        """Returns a string containing the .tbl-formatted entry for the CDS."""
        indices = copy.deepcopy(self.indices)
        phase = self.phase[0]
        return write_tbl_entry(indices, self.strand, has_start, has_stop, True, self.annotations, phase)

