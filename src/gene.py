#!/usr/bin/env python

import math
from src.feature_tbl_entry import FeatureTblEntry

def length_of_segment(index_pair):
    return math.fabs(index_pair[1] - index_pair[0]) + 1

class Gene:

    def __init__(self, seq_name, source, indices, strand, identifier, annotations=None, score=None):
        self.seq_name = seq_name
        self.source = source
        self.indices = indices
        self.score = score
        self.strand = strand
        self.identifier = identifier
        self.mrnas = []
        if not annotations:
            self.annotations = []
        else:
            self.annotations = annotations
        self.death_flagged = False

    def __str__(self):
        result = "Gene (ID=" + str(self.identifier) 
        result += ", seq_name=" + self.seq_name
        result += ") containing " + str(len(self.mrnas))
        result += " mrnas"
        return result

    def get_valid_mrnas(self):
        return [mrna for mrna in self.mrnas if not mrna.death_flagged]
        
    def add_annotation(self, key, value):
        self.annotations.append([key, value])

    def length(self):
        return length_of_segment(self.indices)

    def get_score(self):
        if self.score:
            return self.score
        else:
            return '.'

    def get_longest_exon(self):
        longest = 0
        for mrna in self.get_valid_mrnas():
            length = mrna.get_longest_exon()
            if length > longest:
                longest = length
        return longest

    def get_shortest_exon(self):
        shortest = 0
        for mrna in self.get_valid_mrnas():
            length = mrna.get_shortest_exon()
            if shortest == 0 or length < shortest:
                shortest = length
        return shortest

    def get_total_exon_length(self):
        total = 0
        for mrna in self.get_valid_mrnas():
            total += mrna.get_total_exon_length()
        return total
    
    def get_num_exons(self):
        total = 0
        for mrna in self.get_valid_mrnas():
            total += mrna.get_num_exons()
        return total

    def get_longest_intron(self):
        longest = 0
        for mrna in self.get_valid_mrnas():
            length = mrna.get_longest_intron()
            if length > longest:
                longest = length
        return longest

    def get_shortest_intron(self):
        shortest = 0
        for mrna in self.get_valid_mrnas():
            length = mrna.get_shortest_intron()
            if shortest == 0 or length < shortest:
                shortest = length
        return shortest

    def get_total_intron_length(self):
        total = 0
        for mrna in self.get_valid_mrnas():
            total += mrna.get_total_intron_length()
        return total

    def get_num_introns(self):
        total = 0
        for mrna in self.get_valid_mrnas():
            total += mrna.get_num_introns()
        return total
    
    def clean_up_indices(self):
        if self.indices[1] < 1:
            self.indices[0] = 0
            self.indices[1] = 0
        elif self.indices[0] < 1:
            self.indices[0] = 1
        for mrna in self.mrnas:
            mrna.clean_up_indices()

    def create_starts_and_stops(self, seq_object):
        for mrna in self.mrnas:
            mrna.create_start_and_stop_if_necessary(seq_object, self.strand)

    def remove_first_cds_segment_if_shorter_than(self, min_length):
        if self.mrnas:
            for mrna in self.mrnas:
                mrna.remove_first_cds_segment_if_shorter_than(min_length)

    def remove_invalid_features(self):
        # remove mrnas with indices[0] == 0
        self.mrnas = [m for m in self.mrnas if m.indices[0] != 0]
        for mrna in self.mrnas:
            mrna.remove_invalid_features()

    def length_of_shortest_cds_segment(self):
        min_length = self.mrnas[0].length_of_shortest_cds_segment()
        if len(self.mrnas) == 1:
            return min_length
        else:
            for mrna in self.mrnas:
                if mrna.length_of_shortest_cds_segment() < min_length:
                    min_length = mrna.length_of_shortest_cds_segment()
        return min_length

    def adjust_indices(self, n, start_index=1):
        """Adds 'n' to both indices, checking to ensure that they fall after an optional start index"""
        if self.indices[0] >= start_index:
            self.indices = [i + n for i in self.indices]
        elif self.indices[1] >= start_index:
            self.indices[1] += n
        for mrna in self.mrnas:
            mrna.adjust_indices(n, start_index)

    def invalidate_region(self, start, stop):
        # The beginning is in the invalid region, 
        # trim beginning forward to invalid sequence stop
        if start <= self.indices[0] and stop >= self.indices[0]:
            self.indices[0] = stop+1
        # The end is in the invalid region, trim end back to invalid seq start
        elif start <= self.indices[1] and stop >= self.indices[1]:
            self.indices[1] = start-1

        for mrna in self.mrnas:
            #invalidate_region will return false if the feature doesn't survive invalidation
            if not mrna.cds.invalidate_region(start, stop):
                mrna.death_flagged = True
            if not mrna.exon.invalidate_region(start, stop):
                mrna.death_flagged = True

    def trim_region(self, start, stop):
        """Adjusts indices of gene and its features to account for removal of a seq region.

        If trimmed region intersects an mRNA, the mRNA is removed.
        If trimmed region occurs after the gene, nothing happens."""
        self.indices[0] = self.indices[0]
        self.indices[1] = self.indices[1]
        # Do nothing if trimmed region comes after gene
        if start > self.indices[1]:
            return
        # If trimmed region came before beginning of gene, just adjust indices
        # and call adjust_indices on child mRNAs
        elif stop < self.indices[0]:
            offset = -(stop - start + 1)
            self.adjust_indices(offset)
            for mrna in self.mrnas:
                mrna.adjust_indices(offset)
        # If trimmed region includes gene, be careful.
        # Either it trims the beginning, middle or end of the gene.
        # (Case where entire gene is trimmed should be dealt with by sequence.)
        else:
            # Remove any mRNAs that intersect the trimmed region,
            to_remove = []
            for mrna in self.mrnas:
                if mrna.indices_intersect_mrna([start, stop]):
                    to_remove.append(mrna)
            self.mrnas = [m for m in self.mrnas if m not in to_remove]
            if self.indices[0] >= start and self.indices[0] <= stop and stop <= self.indices[1]: # Beginning of gene is trimmed
                # Move beginning index of gene to one base past the trimmed region
                self.indices[0] = stop + 1
                print("*****")
                print(self.indices[0])
                # Adjust indices on self and remaining mRNAs
                offset = -(stop - start + 1)
                self.adjust_indices(offset)
                for mrna in self.mrnas:
                    mrna.adjust_indices(offset)
            elif self.indices[0] <= start and start <= self.indices[1] and self.indices[1] <= stop: # End of gene is trimmed
                # Move end index of gene to one base before the trimmed region
                offset = -(self.indices[1] - start + 1)
                self.adjust_indices(offset, start) # Will not touch gene_start
            else: # Middle of gene is trimmed
                offset = -(stop - start + 1)
                self.adjust_indices(offset, stop)
                

    def get_partial_info(self):
        results = {"complete": 0, "start_no_stop": 0, "stop_no_start": 0, "no_stop_no_start": 0}
        for mrna in self.get_valid_mrnas():
            if mrna.has_start():
                if mrna.has_stop():
                    results["complete"] += 1
                else:
                    results["start_no_stop"] += 1
            else:
                # No start ...
                if mrna.has_stop():
                    results["stop_no_start"] += 1
                else:
                    results["no_stop_no_start"] += 1
        return results

    def to_gff(self, death_flagged_stuff=False):
        if not death_flagged_stuff and self.death_flagged:
            return ""
    
        result = self.seq_name + "\t" + self.source + "\t"
        result += 'gene' + "\t" + str(self.indices[0]) + "\t"
        result += str(self.indices[1]) + "\t" + self.get_score()
        result += "\t" + self.strand + "\t" + "." + "\t"
        result += "ID=" + str(self.identifier)
        for annot in self.annotations:
            result += ';'+annot[0]+'='+annot[1]
        result += '\n'
        for mrna in self.mrnas:
            result += mrna.to_gff(self.seq_name, self.source, self.strand, death_flagged_stuff)
        return result

    def to_tbl_entries(self, annotator):
        entries = []
        temp_entries = []
        geneEntry = FeatureTblEntry()
        geneEntry.set_type("gene")
        geneEntry.set_name(self.identifier)
        geneEntry.set_seq_name(self.seq_name)
        geneEntry.add_coordinates(self.indices[0], self.indices[1])
        geneEntry.set_strand(self.strand)
        geneEntry.set_phase(0)
        annotator.annotate_gene(geneEntry)

        gene_has_start = True
        gene_has_stop = True
        hypothetical = False

        for mrna in self.mrnas: 
            mrna_entries = mrna.to_tbl_entries(annotator, self.strand)
            for mrna_entry in mrna_entries:
                mrna_entry.set_seq_name(self.seq_name)
                if mrna_entry.is_hypothetical():
                    hypothetical = True
                # If gene contains a partial feature, gene is partial.
                if not mrna_entry.has_start:
                    gene_has_start = False
                if not mrna_entry.has_stop:
                    gene_has_stop = False
                temp_entries.append(mrna_entry)

        geneEntry.set_partial_info(gene_has_start, gene_has_stop) 
        # Hypothetical genes don't get gene names
        if hypothetical == True:
            geneAnnot = geneEntry.get_annotation('gene')
            if geneAnnot:
                geneEntry.add_annotation('note', 'gene '+geneAnnot)
            geneEntry.remove_annotation('gene')

        entries.append(geneEntry)
        entries.extend(temp_entries)
        return entries

    def to_tbl(self):
        if self.death_flagged:
            return ""
    
        if self.strand == "-":
            indices = [self.indices[1], self.indices[0]]
        else:
            indices = self.indices
        output = str(indices[0]) + "\t" + str(indices[1]) + "\t" + "gene\n"
        output += "\t\t\tlocus_tag\t" + self.identifier + "\n"
        for annot in self.annotations:
            output += '\t\t\t'+annot[0]+'\t'+annot[1]+'\n'
        for mrna in self.mrnas:
            output += mrna.to_tbl(self.strand)
        return output



