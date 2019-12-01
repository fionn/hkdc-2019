#!/usr/bin/env python3
"""Unit tests"""

import os
import csv
import pathlib
import unittest

from shapes import Faction, Shape

class TestFaction(unittest.TestCase):
    """Test cases for enumeration"""

    def test_enumeration(self) -> None:
        """Create and compare enums"""
        democracy = Faction.democracy
        establishment = Faction.establishment
        self.assertNotEqual(democracy, establishment)

    def test_enum_map(self) -> None:
        """Test the str -> enum mapping"""
        democracy = Faction.map("democracy")
        establishment = Faction.map("establishment")
        self.assertEqual(democracy, Faction.democracy)
        self.assertEqual(establishment, Faction.establishment)
        self.assertNotEqual(democracy, establishment)

class TestShape(unittest.TestCase):
    """Test cases for Shape"""

    def test_init_kwargs(self) -> None:
        """Initialise Shape with keyword arguments"""
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
        shape = Shape(**kwargs) # type: ignore
        self.assertIsInstance(shape, Shape)

    def test_init_args(self) -> None:
        """Initialise Shape with positional arguments"""
        os.environ["SEARCH_PATH"] = "example/assets/"
        args = [1, "001.jpg", "Wan Chai", "灣仔", 22.279722, 114.171667,
                "B-03", "democracy", 57.76]
        shape = Shape(*args) # type: ignore
        self.assertIsInstance(shape, Shape)

    def test_init_file(self) -> None:
        """Initialise Shape with data file"""
        os.environ["SEARCH_PATH"] = "example/assets/"
        data = pathlib.Path("example/example.csv")
        with data.open() as data_fd:
            data_reader = csv.DictReader(data_fd, dialect="unix")
            shapes = [Shape(**row) for row in data_reader]
        for shape in shapes:
            self.assertIsInstance(shape, Shape)

if __name__ == "__main__":
    unittest.main(verbosity=2)
