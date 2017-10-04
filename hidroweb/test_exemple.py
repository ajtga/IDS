import unittest
from ana_file import AnaFile


class TestingPerformance(unittest.TestCase):
    # I (Augusto) tested the cases we discussed on September 14th.
    # Just made two methods, each tested one version of the get_df method.
    # I made modifications and tested which case was faster, the one that made it is the current in the master branch.

    def test_import1(self):
        # with list(datetime)
        q = AnaFile('QUALAGUA')
        q.get_df_ver1()
        self.assertEqual(q.df['EstacaoCodigo'][0], 48020000)

    def test_import2(self):
        # without list(datetime)
        q = AnaFile('QUALAGUA')
        q.get_df_ver2()
        self.assertEqual(q.df['EstacaoCodigo'][0], 48020000)

    def test_index(self):
        q = AnaFile('QUALAGUA')
        q.get_df_ver1()
        a = q.df
        q.get_df_ver2()
        b = q.df
        self.assertEqual(a.index[0], b.index[0])
