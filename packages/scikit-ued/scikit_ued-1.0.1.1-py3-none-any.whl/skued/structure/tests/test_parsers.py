# -*- coding: utf-8 -*-
import os
import socket
import tempfile
import unittest
from contextlib import suppress
from pathlib import Path
from warnings import filterwarnings

import numpy as np
from spglib import get_symmetry_dataset

from .. import Crystal
from ... import transform
from ..parsers import SKUED_STRUCTURE_CACHE, CIFParser, PDBParser
from ..spg_data import Hall2Number

filterwarnings('ignore', category = UserWarning)

def connection_available():
    """ Returns whether or not an internet connection is available """
    with suppress(OSError):
        try:
            socket.create_connection(("www.google.com", 80))
        except:
            return False
        else:
            return True
    return False

@unittest.skipUnless(connection_available(), "Internet connection is required.")
class TestPDBParser(unittest.TestCase):

    def test_fractional_atoms(self):
        """ Test the PDBParser returns fractional atomic coordinates. """
        with tempfile.TemporaryDirectory() as temp_dir:
            with PDBParser('1fbb', download_dir = temp_dir) as parser:
                for atm in parser.atoms():
                    self.assertLessEqual(atm.coords.max(), 1)
                    self.assertGreaterEqual(atm.coords.min(), 0)
        
    def test_symmetry_operators(self):
        """ Test that the non-translation part of the symmetry_operators is an invertible
        matrix of determinant 1 | -1 """
        with tempfile.TemporaryDirectory() as temp_dir:
            with PDBParser('1fbb', download_dir = temp_dir) as parser:
                for sym_op in parser.symmetry_operators():
                    t = sym_op[:3,:3]
                    self.assertAlmostEqual(abs(np.linalg.det(t)), 1, places = 5)
    
    def test_default_download_dir(self):
        """ Test that the file is saved in the correct temporary directory by default """
        filename = PDBParser.retrieve_pdb_file('1fbb')
        
        self.assertTrue(filename.exists())
        self.assertEqual(filename.parent, SKUED_STRUCTURE_CACHE)

class TestCIFParser(unittest.TestCase):
    """ Test the CIFParser on all CIF files stored herein """

    def _cif_files(self):
        """ Yields cif files included in scikit-ued """
        for root, _, files in os.walk(os.path.join('skued', 'structure')):
            for name in filter(lambda path: path.endswith('.cif'), files):
                yield os.path.join(root, name)

    def test_compatibility(self):
        """ Test the CIFParser on all CIF files stored herein to check build errors"""
        for name in self._cif_files():
            with self.subTest(name.split('\\')[-1]):
                c = Crystal.from_cif(name)

    def test_fractional_atoms(self):
        """ Test the CIFParser returns fractional atomic coordinates. """
        for name in self._cif_files():
            with self.subTest(name.split('\\')[-1]):
                with CIFParser(name) as p:
                    for atm in p.atoms():
                        self.assertLessEqual(atm.coords.max(), 1)
                        self.assertGreaterEqual(atm.coords.min(), 0)
    
    def test_symmetry_operators(self):
        """ Test that the non-translation part of the symmetry_operators is an invertible
        matrix of determinant 1 | -1 """
        for name in self._cif_files():
            with self.subTest(name.split('\\')[-1]):
                with CIFParser(name) as p:
                    for sym_op in p.symmetry_operators():
                        t = sym_op[:3,:3]
                        self.assertAlmostEqual(abs(np.linalg.det(t)), 1)
    
    def test_international_number(self):
        """ Test that the international space group number  found by 
        CIFParser is the same as spglib's """
        for name in self._cif_files():
            with self.subTest(name.split('\\')[-1]):
                with CIFParser(name) as p:
                    from_parser = Hall2Number[p.hall_symbol()]
                    
                    crystal = Crystal.from_cif(name)
                    from_spglib = crystal.spacegroup_info()['international_number']
                    self.assertEqual(from_parser, from_spglib)
    
    def test_silicon(self):
        """ Test CIFParser on Si.cif (diamond structure) """
        Si_path = os.path.join('skued', 'structure', 'cifs', 'Si.cif')
        si = Crystal.from_cif(Si_path)

        self.assertEqual(len(si), 8)
    
    def test_vo2(self):
        """ Test CIFParser on vo2.cif (monoclinic M1) """
        VO2_path = os.path.join('skued', 'structure', 'cifs', 'vo2-m1.cif')
        vo2 = Crystal.from_cif(VO2_path)

        self.assertEqual(len(vo2), 12)
        self.assertSequenceEqual(vo2.lattice_parameters, 
                                 (5.7430000000000003, 4.5170000000000003, 5.375, 90.0, 122.60000000000001, 90.0))
        self.assertAlmostEqual(vo2.volume, 117.4661530) # from cif2cell   

if __name__ == '__main__':
    unittest.main()
