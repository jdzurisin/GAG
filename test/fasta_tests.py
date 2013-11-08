#!/usr/bin/env python

import unittest
from src.fasta import Fasta
from src.bed import Bed
from mock import Mock

class TestFasta(unittest.TestCase):

    def setUp(self):
        self.fasta0 = Fasta()
        self.fasta1 = Fasta()
        self.fasta1.read_string('>seq1\nATGCCGTA\n>seq2\nAGGTCC\n>seq3\nGGGGGG')

    def test_constructor(self):
        self.assertEqual('Fasta', self.fasta0.__class__.__name__)
        self.assertTrue(isinstance(self.fasta0.entries, list))

    def test_read_string(self):
        self.assertEquals(0, len(self.fasta0.entries))
        self.fasta0.read_string('>seq1\nATGCCGTA\n>seq2\nAGGTCC\n>seq3\nGGGGGG')
        self.assertEquals(3, len(self.fasta0.entries))

    def test_trim_seq(self):
        self.fasta1.trim_seq('seq2', 2, 3)
        expected = '>seq1\nATGCCGTA\n>seq2\nATCC\n>seq3\nGGGGGG'
        self.assertEqual(expected, self.fasta1.write_string())
        self.fasta1.trim_seq('seq2', 1, 4)
        expected = '>seq1\nATGCCGTA\n>seq3\nGGGGGG'
        self.assertEqual(expected, self.fasta1.write_string())

    def test_read_file(self):
        self.fasta0.read_file("sample_files/no_line_breaks.fasta")
        self.assertEquals(2, len(self.fasta0.entries))
        self.assertEquals('seq_1', self.fasta0.entries[0][0])
        self.assertEquals('GATTACAGATTACAGATTACAGATTACAGATTACAGATTACAGATTACAGATTACA', self.fasta0.entries[0][1])
        self.assertEquals('seq_2', self.fasta0.entries[1][0])
        self.assertEquals('NNNNNNNNGATTACAGATTACAGATTACANNNNNNNNNNN', self.fasta0.entries[1][1])
        self.fasta0.read_file("sample_files/has_line_breaks.fasta")
        self.assertEquals(4, len(self.fasta0.entries))
        self.assertEquals(['seq_1', 'GATTACAGATTACAGATTACAGATTACAGATTACAGATTACAGATTACAGATTACA'], self.fasta0.entries[2])
        self.assertEquals(['seq_2', 'NNNNNNNNGATTACAGATTACAGATTACANNNNNNNNNNN'], self.fasta0.entries[3])

    def test_apply_bed(self):
        bed = Bed({'seq1': [2,7], 'seq3': [2,6]})
        self.assertEquals('ATGCCGTA', self.fasta1.entries[0][1])
        self.assertEquals('GGGGGG', self.fasta1.entries[2][1])
        self.fasta1.apply_bed(bed)
        self.assertEquals('TGCCGT', self.fasta1.entries[0][1])
        self.assertEquals('GGGGG', self.fasta1.entries[2][1])
        newbed = Bed({'seq3': [0, 0]})
        self.assertEquals(3, len(self.fasta1.entries))
        self.fasta1.apply_bed(newbed)
        self.assertEquals(2, len(self.fasta1.entries))
        


##########################
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFasta))
    return suite

if __name__ == '__main__':
    unittest.main()
