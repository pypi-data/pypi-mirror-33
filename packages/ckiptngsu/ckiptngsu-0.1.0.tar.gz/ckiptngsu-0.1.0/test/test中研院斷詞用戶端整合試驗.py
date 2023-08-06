# -*- coding: utf-8 -*-
from unittest.case import TestCase
from ckip import 斷詞


class 中研院斷詞用戶端整合試驗(TestCase):
    def test_語句斷空字串(self):
        self.assertEqual(斷詞(''), [])

    def test_語句斷空白佮換逝(self):
        self.assertEqual(斷詞('\n \n'), [])

    def test_語句斷一句話(self):
        self.assertEqual(斷詞('我想吃飯。'), [[
            '\u3000我(N)\u3000想(Vt)\u3000吃飯(Vi)\u3000。(PERIODCATEGORY)',
        ]])

    def test_語句斷一句話閣換逝(self):
        self.assertEqual(斷詞('我想吃飯。\n'), [[
            '\u3000我(N)\u3000想(Vt)\u3000吃飯(Vi)\u3000。(PERIODCATEGORY)',
        ]])

    def test_語句斷一逝字(self):
        self.assertEqual(斷詞('我想吃飯。我想吃很多飯。'), [[
            '\u3000我(N)\u3000想(Vt)\u3000吃飯(Vi)\u3000。(PERIODCATEGORY)',
            '\u3000我(N)\u3000想(Vt)\u3000吃(Vt)\u3000很多(DET)\u3000飯(N)\u3000。(PERIODCATEGORY)',
        ]])

    def test_語句斷兩逝字(self):
        self.assertEqual(斷詞('我想吃飯。我想吃很多飯。\n我吃飽了。'), [
            [
                '\u3000我(N)\u3000想(Vt)\u3000吃飯(Vi)\u3000。(PERIODCATEGORY)',
                '\u3000我(N)\u3000想(Vt)\u3000吃(Vt)\u3000很多(DET)\u3000飯(N)\u3000。(PERIODCATEGORY)',
            ],
            [
                '\u3000我(N)\u3000吃飽(Vi)\u3000了(T)\u3000。(PERIODCATEGORY)',
            ]
        ])

    def test_語句斷濟逝字(self):
        self.assertEqual(斷詞('\n\n我想吃飯。我想吃很多飯。\n\n  \n\n  　 \n\n我吃飽了。\n\n'), [
            [
                '\u3000我(N)\u3000想(Vt)\u3000吃飯(Vi)\u3000。(PERIODCATEGORY)',
                '\u3000我(N)\u3000想(Vt)\u3000吃(Vt)\u3000很多(DET)\u3000飯(N)\u3000。(PERIODCATEGORY)',
            ],
            [
                '\u3000我(N)\u3000吃飽(Vi)\u3000了(T)\u3000。(PERIODCATEGORY)',
            ]
        ])

    def test_語句斷大於符號(self):
        self.assertEqual(斷詞('我想) :>'), [[
            '\u3000我(N)\u3000想(Vt)\u3000)(PARENTHESISCATEGORY)\u3000:(COLONCATEGORY)\u3000&gt;(PARENTHESISCATEGORY)'
        ]])

    def test_語句斷小於符號的空白結果(self):
        self.assertEqual(斷詞('我想) :<'), [[]])
