#!/usr/bin/env python3
"""Geographical shapes"""

import os
import csv
import enum
import random
import logging
import argparse
from pathlib import Path
from typing import NamedTuple

import tweepy


def configure_logger(module_name: str) -> logging.Logger:
    """Configure the logger"""
    logger = logging.getLogger(module_name)
    formatter = logging.Formatter(fmt="%(levelname)s: %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

LOG = configure_logger(__name__)

@enum.unique
class Faction(enum.Enum):
    """Enumeration of political camps"""
    democracy = 1
    establishment = 2

    class DCWinnerError(Exception):
        """Raise on failed enumeration"""

    @classmethod
    def map(cls, identifier: str) -> "Faction":
        """Map identifiers to enumerations"""
        if identifier == "democracy":
            return cls.democracy
        if identifier == "establishment":
            return cls.establishment
        raise cls.DCWinnerError(f"Can't enumerate {identifier}")

# pylint: disable=too-few-public-methods,too-many-instance-attributes
class Shape:
    """Shape object"""

    Caption = NamedTuple("Caption", [("en", str), ("zh", str)])
    Coordinates = NamedTuple("Coordinates", [("lat", float), ("long", float)])

    # pylint: disable=too-many-arguments
    def __init__(self, sort: int, filename: str, caption_en: str,
                 caption_zh: str, latitude: float, longitude: float,
                 electoral_code: str, dc_winner: str,
                 percentage_democracy: float) -> None:
        self._search_path = Path(os.environ["SEARCH_PATH"])
        self.sort = int(sort)
        self.file = Path(self._search_path / filename).resolve(strict=True)
        self.caption = self.Caption(caption_en, caption_zh)
        self.geo = self.Coordinates(float(latitude), float(longitude))
        self.electoral_code = electoral_code
        self.dc_winner = Faction.map(dc_winner)
        self.percentage_democracy = percentage_democracy

    def __repr__(self) -> str:
        return f"Shape{self.sort, self.file.name, *self.caption, *self.geo}"

class Twitter:
    """Wrapper for the Twitter API"""

    def __init__(self) -> None:
        auth = tweepy.OAuthHandler(os.environ["API_KEY"],
                                   os.environ["API_SECRET"])
        auth.set_access_token(os.environ["ACCESS_TOKEN"],
                              os.environ["ACCESS_TOKEN_SECRET"])
        self.api = tweepy.API(auth, wait_on_rate_limit=True,
                              wait_on_rate_limit_notify=True)

    @staticmethod
    def _compose(shape: Shape) -> dict:
        """Compose a status dictionary compatible with api.status_update"""
        text = f"{shape.caption.en}, {shape.caption.zh}."
        return {"status": text, "lat": shape.geo.lat, "long": shape.geo.long}

    def update(self, shape: Shape) -> tweepy.Status:
        """Post tweet for shape"""
        composition = self._compose(shape)
        LOG.info("Selecting %s", composition["status"])

        with shape.file.open("rb") as shape_fd:
            media = self.api.media_upload(filename=shape.file.name,
                                          file=shape_fd)

        # Not implemented yet, wait for > v3.8.0
        #self.api.create_media_metadata(media.media_id, f"{shape.caption.en}")
        return self.api.update_status(**composition, media_ids=[media.media_id])

def main() -> None:
    """Entry point"""
    parser = argparse.ArgumentParser(description="Tweet shapes")
    parser.add_argument("data", type=Path, metavar="CSV_FILE",
                        help="path to CSV data file")
    args = parser.parse_args()

    with args.data.open() as data_fd:
        data_reader = csv.DictReader(data_fd, delimiter=",", dialect="unix")
        shapes = [Shape(**row) for row in data_reader]

    twitter = Twitter()

    shape = random.choice(shapes)
    tweet = twitter.update(shape)

    LOG.info("\"%s\" from %s", tweet.text, tweet.place.full_name)

if __name__ == "__main__":
    main()
