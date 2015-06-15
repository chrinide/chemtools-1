import os
import unittest
from chemtools import basisset
from chemtools.basisset import BasisSet

class TestSequenceFunctions(unittest.TestCase):

    def test_eventemp_if_nf_is_integer(self):
        self.assertRaises(TypeError, basisset.eventemp, (0.0, (1.0, 2.0)))

    def test_eventemp_if_number_of_params_is_2(self):
        self.assertRaises(ValueError, basisset.eventemp, 2, (1.0, 2.0, 3.0))

    def test_eventemp_zero_nf(self):
        self.assertListEqual(basisset.eventemp(0, (1.0, 2.0)), [])

    def test_eventemp_small(self):
        self.assertListEqual(basisset.eventemp(1, (2.0, 3.0)), [2.0])

    def test_eventemp_medium(self):
        self.assertListEqual(basisset.eventemp(4, (0.5, 2.0)), [0.5, 1.0, 2.0, 4.0])

    def test_welltemp_if_nf_is_integer(self):
        self.assertRaises(TypeError, basisset.welltemp, (0.0, (1.0, 2.0, 3.0, 4.0)))

    def test_welltemp_if_number_of_params_is_4(self):
        self.assertRaises(ValueError, basisset.welltemp, 2, (1.0, 2.0, 3.0, 4.0, 5.0))

    def test_welltemp_zero_nf(self):
        self.assertListEqual(basisset.welltemp(0, (1.0, 2.0, 3.0, 4.0)), [])

    def test_welltemp_small(self):
        self.assertListEqual(basisset.welltemp(1, (1.0, 2.0, 3.0, 4.0)), [4.0])

    def test_welltemp_medium(self):
        self.assertListEqual(basisset.welltemp(4, (0.5, 2.0, 3.0, 4.0)), [0.505859375, 1.1875, 3.8984375, 16.0])

    def test_legendre_if_nf_is_integer(self):
        self.assertRaises(TypeError, basisset.legendre, (0.0, (1.0, 2.0, 3.0, 4.0)))

    def test_legendre_if_number_of_params_is_at_least_1(self):
        self.assertRaises(ValueError, basisset.legendre, 2, ())

    def test_legendre_zero_nf(self):
        self.assertListEqual(basisset.legendre(0, (1.0, 2.0, 3.0, 4.0)), [])

    def test_legendre_small(self):
        self.assertListEqual(basisset.legendre(2, (1.0, 1.0)), [1.0, 7.3890560989306504])

    def test_legendre_medium(self):
        self.assertListEqual(basisset.legendre(4, (1.0, 1.2, 1.5)), [3.6692966676192444, 1.1051709180756477, 2.459603111156949, 40.447304360067399])

class TestBasisSetInitialization(unittest.TestCase):

    def test_init_eventemp_s(self):

        f = [('s', 5, (0.5, 2.0)), ('p', 4, (1.0, 3.0))]
        bs = BasisSet.from_sequence(formula='eventemp', functs=f, element='H', name='small et')
        self.assertIsInstance(bs, BasisSet)
        self.assertEqual(bs.name, 'small et')
        self.assertEqual(bs.element, 'H')
        self.assertAlmostEqual(bs.functions['s']['e'], [0.5, 1.0, 2.0, 4.0, 8.0])

    def test_init_eventemp_sp(self):

        f = [('s', 5, (0.5, 2.0)), ('p', 4, (1.0, 3.0))]
        bs = BasisSet.from_sequence(formula='eventemp', functs=f, element='H', name='small et')
        self.assertIsInstance(bs, BasisSet)
        self.assertAlmostEqual(bs.functions['s']['e'], [0.5, 1.0, 2.0, 4.0, 8.0])
        self.assertAlmostEqual(bs.functions['p']['e'], [1.0, 3.0, 9.0, 27.0])

    def test_init_eventemp_df(self):

        f = [('d', 4, (0.5, 2.0)), ('f', 3, (1.0, 3.0))]
        bs = BasisSet.from_sequence(formula='eventemp', functs=f, element='H', name='small et')
        self.assertIsInstance(bs, BasisSet)
        self.assertAlmostEqual(bs.functions['d']['e'], [0.5, 1.0, 2.0, 4.0])
        self.assertAlmostEqual(bs.functions['f']['e'], [1.0, 3.0, 9.0])

    def test_init_welltemp_s(self):

        f = [('s', 4, (0.5, 2.0, 3.0, 4.0))]
        bs = BasisSet.from_sequence(formula='welltemp', functs=f, element='H', name='small wt')
        self.assertIsInstance(bs, BasisSet)
        self.assertAlmostEqual(bs.functions['s']['e'], [0.505859375, 1.1875, 3.8984375, 16.0])

    def test_init_welltemp_sp(self):

        wt_s = [0.55241203390786842, 1.2408224685280691, 2.7834955069665117,
                6.2130589875561473, 13.785155024015765, 30.399999999999999]
        wt_p = [0.54936270901760076, 1.8646357406075393, 6.3531011529592449,
                21.580546589187453, 72.900000000000006]
        f = [('s', 6, (0.5, 2.0, 0.9, 1.2)), ('p', 5, (0.5, 3.0, 0.8, 1.3))]
        bs = BasisSet.from_sequence(formula='welltemp', functs=f, element='H', name='small wt')
        self.assertIsInstance(bs, BasisSet)
        self.assertAlmostEqual(bs.functions['s']['e'], wt_s)
        self.assertAlmostEqual(bs.functions['p']['e'], wt_p)

    def test_init_legendre_s(self):

        le_s = [0.36787944117144233, 1.3956124250860895, 5.2944900504700287,
                20.085536923187668]

        f = [('s', 4, (1.0, 2.0))]
        bs = BasisSet.from_sequence(formula='legendre', functs=f, element='H', name='small et')
        self.assertIsInstance(bs, BasisSet)
        self.assertAlmostEqual(bs.functions['s']['e'], le_s)

    def test_init_legendre_spd(self):

        leg_s = [0.12245642825298195, 0.65376978512984729, 1.2214027581601699,
                 7.5761109446368486, 1480.2999275845475]
        leg_p = [1.8221188003905087, 4.7027533114762283, 5.2166313162210942,
                 330.29955990964862]
        leg_d = [1.8221188003905091, 1.5683121854901687, 36.59823444367801]
        f = [('s', 5, (1.0, 3.5, 1.6, 1.2)), ('p', 4, (2.0, 1.5, 1.2, 1.1)), ('d', 3, (1.0, 1.5, 1.1))]
        bs = BasisSet.from_sequence(formula='legendre', functs=f, element='H', name='small et')
        self.assertIsInstance(bs, BasisSet)
        self.assertAlmostEqual(bs.functions['s']['e'], leg_s)
        self.assertAlmostEqual(bs.functions['p']['e'], leg_p)
        self.assertAlmostEqual(bs.functions['d']['e'], leg_d)

    def test_init_mixed_formula_spd(self):

        et_s = [0.5, 1.0, 2.0, 4.0, 8.0]
        wt_p = [0.505859375, 1.1875, 3.8984375, 16.0]
        leg_d = [1.8221188003905091, 1.5683121854901687, 36.59823444367801]
        formulas = ['even', 'well', 'legendre']
        f = [('s', 5, (0.5, 2.0)), ('p', 4, (0.5, 2.0, 3.0, 4.0)), ('d', 3, (1.0, 1.5, 1.1))]
        bs = BasisSet.from_sequence(formula=formulas, functs=f, element='H', name='small et')
        self.assertIsInstance(bs, BasisSet)
        self.assertAlmostEqual(bs.functions['s']['e'], et_s)
        self.assertAlmostEqual(bs.functions['p']['e'], wt_p)
        self.assertAlmostEqual(bs.functions['d']['e'], leg_d)

class TestBasisSetPrintingFormats(unittest.TestCase):

    def setUp(self):

        fs = [('s', 4, (0.5, 2.0)), ('p', 3, (1.0, 3.0)), ('d', 2, (1.5, 4.0))]
        self.bs = BasisSet.from_sequence(name='test', element='H', functs=fs, formula='even')
        self.bs.uncontract()

    def tearDown(self):
        del self.bs

    def test_printing_to_gamess(self):

        bsstr = '''S  1
  1        0.5000000000     1.00000000
S  1
  1        1.0000000000     1.00000000
S  1
  1        2.0000000000     1.00000000
S  1
  1        4.0000000000     1.00000000
P  1
  1        1.0000000000     1.00000000
P  1
  1        3.0000000000     1.00000000
P  1
  1        9.0000000000     1.00000000
D  1
  1        1.5000000000     1.00000000
D  1
  1        6.0000000000     1.00000000

'''
        self.assertEqual(self.bs.to_gamess(), bsstr)

    def test_printing_to_molpro(self):

        bsstr = '''s, H, 0.5000000000, 1.0000000000, 2.0000000000, 4.0000000000
c, 1.1, 1.00000000
c, 2.2, 1.00000000
c, 3.3, 1.00000000
c, 4.4, 1.00000000
p, H, 1.0000000000, 3.0000000000, 9.0000000000
c, 1.1, 1.00000000
c, 2.2, 1.00000000
c, 3.3, 1.00000000
d, H, 1.5000000000, 6.0000000000
c, 1.1, 1.00000000
c, 2.2, 1.00000000
'''
        self.assertEqual(self.bs.to_molpro(), bsstr)


    def test_printing_to_cfour(self):

        bsstr = '''
H:test


  3
    0    1    2
    4    3    2
    4    3    2

     0.50000000     1.00000000     2.00000000     4.00000000

     1.00000000     0.00000000     0.00000000     0.00000000
     0.00000000     1.00000000     0.00000000     0.00000000
     0.00000000     0.00000000     1.00000000     0.00000000
     0.00000000     0.00000000     0.00000000     1.00000000

     1.00000000     3.00000000     9.00000000

     1.00000000     0.00000000     0.00000000
     0.00000000     1.00000000     0.00000000
     0.00000000     0.00000000     1.00000000

     1.50000000     6.00000000

     1.00000000     0.00000000
     0.00000000     1.00000000

'''
        self.assertEqual(self.bs.to_cfour(), bsstr)

    def test_printing_to_dalton(self):

        bsstr = '''! test
! s functions
F   4   4
        0.5000000000     1.00000000     0.00000000     0.00000000     0.00000000
        1.0000000000     0.00000000     1.00000000     0.00000000     0.00000000
        2.0000000000     0.00000000     0.00000000     1.00000000     0.00000000
        4.0000000000     0.00000000     0.00000000     0.00000000     1.00000000
! p functions
F   3   3
        1.0000000000     1.00000000     0.00000000     0.00000000
        3.0000000000     0.00000000     1.00000000     0.00000000
        9.0000000000     0.00000000     0.00000000     1.00000000
! d functions
F   2   2
        1.5000000000     1.00000000     0.00000000
        6.0000000000     0.00000000     1.00000000
'''
        self.assertEqual(self.bs.to_dalton(), bsstr)

    def test_printing_to_nwchem(self):

        bsstr = '''BASIS "ao basis" PRINT
H s
        0.5000000000     1.00000000     0.00000000     0.00000000     0.00000000
        1.0000000000     0.00000000     1.00000000     0.00000000     0.00000000
        2.0000000000     0.00000000     0.00000000     1.00000000     0.00000000
        4.0000000000     0.00000000     0.00000000     0.00000000     1.00000000
H p
        1.0000000000     1.00000000     0.00000000     0.00000000
        3.0000000000     0.00000000     1.00000000     0.00000000
        9.0000000000     0.00000000     0.00000000     1.00000000
H d
        1.5000000000     1.00000000     0.00000000
        6.0000000000     0.00000000     1.00000000
END
'''
        self.assertEqual(self.bs.to_nwchem(), bsstr)

class TestBasisSetParsingMolpro(unittest.TestCase):

    def setUp(self):
        self.basstr = '''basis={
!
! HYDROGEN       (5s,2p) -> [3s,2p]
! HYDROGEN       (4s,1p) -> [2s,1p]
! HYDROGEN       (1s,1p)
s, H , 13.0100000, 1.9620000, 0.4446000, 0.1220000, 0.0297400
c, 1.3, 0.0196850, 0.1379770, 0.4781480
c, 4.4, 1
c, 5.5, 1
p, H , 0.7270000, 0.1410000
c, 1.1, 1
c, 2.2, 1
! LITHIUM       (10s,5p,2d) -> [4s,3p,2d]
! LITHIUM       (9s,4p,1d) -> [3s,2p,1d]
! LITHIUM       (1s,1p,1d)
s, LI , 1469.0000000, 220.5000000, 50.2600000, 14.2400000, 4.5810000, 1.5800000, 0.5640000, 0.0734500, 0.0280500, 0.0086400
c, 1.8, 0.0007660, 0.0058920, 0.0296710, 0.1091800, 0.2827890, 0.4531230, 0.2747740, 0.0097510
c, 1.8, -0.0001200, -0.0009230, -0.0046890, -0.0176820, -0.0489020, -0.0960090, -0.1363800, 0.5751020
c, 9.9, 1
c, 10.10, 1
p, LI , 1.5340000, 0.2749000, 0.0736200, 0.0240300, 0.0057900
c, 1.3, 0.0227840, 0.1391070, 0.5003750
c, 4.4, 1
c, 5.5, 1
d, LI , 0.1239000, 0.0725000
c, 1.1, 1
c, 2.2, 1
! BERYLLIUM       (10s,5p,2d) -> [4s,3p,2d]
! BERYLLIUM       (9s,4p,1d) -> [3s,2p,1d]
! BERYLLIUM       (1s,1p,1d)
s, BE , 2940.0000000, 441.2000000, 100.5000000, 28.4300000, 9.1690000, 3.1960000, 1.1590000, 0.1811000, 0.0589000, 0.0187700
c, 1.8, 0.0006800, 0.0052360, 0.0266060, 0.0999930, 0.2697020, 0.4514690, 0.2950740, 0.0125870
c, 1.8, -0.0001230, -0.0009660, -0.0048310, -0.0193140, -0.0532800, -0.1207230, -0.1334350, 0.5307670
c, 9.9, 1
c, 10.10, 1
p, BE , 3.6190000, 0.7110000, 0.1951000, 0.0601800, 0.0085000
c, 1.3, 0.0291110, 0.1693650, 0.5134580
c, 4.4, 1
c, 5.5, 1
d, BE , 0.2380000, 0.0740000
c, 1.1, 1
c, 2.2, 1
}'''

        self.fname = 'test.bas'
        self.fpath = os.path.join(os.getcwd(), self.fname)
        with open(self.fpath, 'w') as fil:
            fil.write(self.basstr)

        def tearDown(self):
            os.remove(self.fpath)

    def test_parse_molpro_format(self):

        bsd = BasisSet.from_file(self.fname, fmt='molpro')
        self.assertIsInstance(bsd, dict)
        self.assertIn('H', bsd.keys())
        self.assertIn('Li', bsd.keys())
        self.assertIn('Be', bsd.keys())
        self.assertIsInstance(bsd['H'], BasisSet)
        self.assertIsInstance(bsd['Li'], BasisSet)
        self.assertIsInstance(bsd['Be'], BasisSet)
        self.assertEqual(bsd['H'].nf(), 9)
        self.assertEqual(bsd['Li'].nf(), 23)
        self.assertEqual(bsd['Be'].nf(), 23)

class TestBasisSetParsingGamess(unittest.TestCase):

    def setUp(self):

        self.basstr = '''$DATA
HYDROGEN
S   3
  1     13.0100000              0.0196850        
  2      1.9620000              0.1379770        
  3      0.4446000              0.4781480        
S   1
  1      0.1220000              1.0000000        
S   1
  1      0.0297400              1.0000000        
P   1
  1      0.7270000              1.0000000        
P   1
  1      0.1410000              1.0000000        

LITHIUM
S   8
  1   1469.0000000              0.0007660        
  2    220.5000000              0.0058920        
  3     50.2600000              0.0296710        
  4     14.2400000              0.1091800        
  5      4.5810000              0.2827890        
  6      1.5800000              0.4531230        
  7      0.5640000              0.2747740        
  8      0.0734500              0.0097510        
S   8
  1   1469.0000000             -0.0001200        
  2    220.5000000             -0.0009230        
  3     50.2600000             -0.0046890        
  4     14.2400000             -0.0176820        
  5      4.5810000             -0.0489020        
  6      1.5800000             -0.0960090        
  7      0.5640000             -0.1363800        
  8      0.0734500              0.5751020        
S   1
  1      0.0280500              1.0000000        
S   1
  1      0.0086400              1.0000000        
P   3
  1      1.5340000              0.0227840        
  2      0.2749000              0.1391070        
  3      0.0736200              0.5003750        
P   1
  1      0.0240300              1.0000000        
P   1
  1      0.0057900              1.0000000        
D   1
  1      0.1239000              1.0000000        
D   1
  1      0.0725000              1.0000000        

BERYLLIUM
S   8
  1   2940.0000000              0.0006800        
  2    441.2000000              0.0052360        
  3    100.5000000              0.0266060        
  4     28.4300000              0.0999930        
  5      9.1690000              0.2697020        
  6      3.1960000              0.4514690        
  7      1.1590000              0.2950740        
  8      0.1811000              0.0125870        
S   8
  1   2940.0000000             -0.0001230        
  2    441.2000000             -0.0009660        
  3    100.5000000             -0.0048310        
  4     28.4300000             -0.0193140        
  5      9.1690000             -0.0532800        
  6      3.1960000             -0.1207230        
  7      1.1590000             -0.1334350        
  8      0.1811000              0.5307670        
S   1
  1      0.0589000              1.0000000        
S   1
  1      0.0187700              1.0000000        
P   3
  1      3.6190000              0.0291110        
  2      0.7110000              0.1693650        
  3      0.1951000              0.5134580        
P   1
  1      0.0601800              1.0000000        
P   1
  1      0.0085000              1.0000000        
D   1
  1      0.2380000              1.0000000        
D   1
  1      0.0740000              1.0000000        
$END'''

        self.fname = 'test.bas'
        self.fpath = os.path.join(os.getcwd(), self.fname)
        with open(self.fpath, 'w') as fil:
            fil.write(self.basstr)

        def tearDown(self):
            os.remove(self.fpath)

    def test_parse_gamess_format(self):

        bsd = BasisSet.from_file(self.fname, fmt='gamessus')
        self.assertIsInstance(bsd, dict)
        self.assertIn('H', bsd.keys())
        self.assertIn('Li', bsd.keys())
        self.assertIn('Be', bsd.keys())
        self.assertIsInstance(bsd['H'], BasisSet)
        self.assertIsInstance(bsd['Li'], BasisSet)
        self.assertIsInstance(bsd['Be'], BasisSet)
        self.assertEqual(bsd['H'].nf(), 9)
        self.assertEqual(bsd['Li'].nf(), 23)
        self.assertEqual(bsd['Be'].nf(), 23)

if __name__ == "__main__":
    unittest.main()
