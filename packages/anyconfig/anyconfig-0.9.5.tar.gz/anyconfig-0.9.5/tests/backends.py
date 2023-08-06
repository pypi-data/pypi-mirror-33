#
# Copyright (C) 2012 - 2015 Satoru SATOH <ssato @ redhat.com>
# License: MIT
#
# pylint: disable=missing-docstring, invalid-name, protected-access
from __future__ import absolute_import

import os.path
import unittest
import anyconfig.backend.json
import anyconfig.backends as TT
import anyconfig.ioinfo

from anyconfig.compat import pathlib
from anyconfig.globals import UnknownParserTypeError, UnknownFileTypeError


CNF_PATH = os.path.join(os.path.dirname(__file__), "00-cnf.json")


class Test(unittest.TestCase):

    def test_10_list_types(self):
        types = TT.list_types()

        self.assertTrue(isinstance(types, list))
        self.assertTrue(bool(list))  # ensure it's not empty.

    def test_20_find_parser_by_type__ng_cases(self):
        self.assertRaises(ValueError, TT.find_parser_by_type, None)
        self.assertRaises(UnknownParserTypeError, TT.find_parser_by_type,
                          "_unkonw_type_")

    def test_22_find_parser_by_type(self):
        self.assertTrue(isinstance(TT.find_parser_by_type("json"),
                                   anyconfig.backend.json.Parser))

    def test_30_find_parser_ng_cases(self):
        self.assertRaises(ValueError, TT.find_parser, None)
        self.assertRaises(UnknownParserTypeError, TT.find_parser, None,
                          "_unkonw_type_")
        self.assertRaises(UnknownFileTypeError, TT.find_parser,
                          "cnf.unknown_ext")

    def test_32_find_parser_ng_cases(self):
        pcls = anyconfig.backend.json.Parser
        self.assertTrue(isinstance(TT.find_parser("x.conf",
                                                  forced_type="json"),
                                   pcls))
        self.assertTrue(isinstance(TT.find_parser("x.json"), pcls))

        cnf = os.path.join(os.path.dirname(__file__), "00-cnf.json")
        with open(cnf) as inp:
            self.assertTrue(isinstance(TT.find_parser(inp), pcls))

        if pathlib is not None:
            inp = pathlib.Path("x.json")
            self.assertTrue(isinstance(TT.find_parser(inp), pcls))

    def test_34_find_parser__input_object(self):
        inp = anyconfig.ioinfo.make(CNF_PATH,
                                    TT._PARSERS_BY_EXT, TT._PARSERS_BY_TYPE)
        psr = TT.find_parser(inp)
        self.assertTrue(isinstance(psr, anyconfig.backend.json.Parser))

# vim:sw=4:ts=4:et:
