#!/usr/bin/env python3
"""Unit tests"""

import os
import csv
import pathlib
import unittest

from constituencies import Faction, Constituency

class TestFaction(unittest.TestCase):
    """Test cases for enumeration"""

    def test_enumeration(self) -> None:
        """Create and compare enums"""
        democracy = Faction.democracy
        establishment = Faction.establishment
        nonpartisan = Faction.nonpartisan
        self.assertNotEqual(democracy, establishment)
        self.assertNotEqual(democracy, nonpartisan)
        self.assertNotEqual(establishment, nonpartisan)

    def test_enum_map(self) -> None:
        """Test the str -> enum mapping"""
        democracy = Faction.map("democracy")
        establishment = Faction.map("establishment")
        nonpartisan = Faction.map("nonpartisan")
        self.assertEqual(democracy, Faction.democracy)
        self.assertEqual(establishment, Faction.establishment)
        self.assertEqual(nonpartisan, Faction.nonpartisan)
        self.assertNotEqual(democracy, establishment)
        self.assertNotEqual(democracy, nonpartisan)
        self.assertNotEqual(establishment, nonpartisan)

    def test_enum_bad_identifier(self) -> None:
        """Test raising Faction.MappingError"""
        with self.assertRaises(ValueError):
            Faction.map("yolo")

class TestConstituency(unittest.TestCase):
    """Test cases for Constituency"""

    def test_init_kwargs(self) -> None:
        """Initialise Constituency with keyword arguments"""
        os.environ["SEARCH_PATH"] = "example/assets/"
        kwargs = {"sort": 1,
                  "filename": "001.jpg",
                  "caption_en": "Wan Chai",
                  "caption_zh": "灣仔",
                  "latitude": 22.279722,
                  "longitude": 114.171667,
                  "electoral_code": "B-03",
                  "dc_winner": "democracy",
                  "percentage_democracy": 57.76}
        constituency = Constituency(**kwargs) # type: ignore
        self.assertIsInstance(constituency, Constituency)

    def test_init_args(self) -> None:
        """Initialise Constituency with positional arguments"""
        os.environ["SEARCH_PATH"] = "example/assets/"
        args = [1, "001.jpg", "Wan Chai", "灣仔", 22.279722, 114.171667,
                "B-03", "democracy", 57.76]
        constituency = Constituency(*args) # type: ignore
        self.assertIsInstance(constituency, Constituency)

    def test_init_file(self) -> None:
        """Initialise Constituency with data file"""
        os.environ["SEARCH_PATH"] = "example/assets/"
        data = pathlib.Path("example/example.csv")
        with data.open() as data_fd:
            data_reader = csv.DictReader(data_fd, dialect="unix")
            constituencies = [Constituency(**row) for row in data_reader]
        for constituency in constituencies:
            self.assertIsInstance(constituency, Constituency)

if __name__ == "__main__":
    unittest.main(verbosity=2)
