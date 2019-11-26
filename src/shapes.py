#!/usr/bin/env python3
"""Geographical shapes"""

import os
import csv
import random
import logging
import argparse
from pathlib import Path
from typing import NamedTuple

import tweepy

SEARCH_PATH = Path(os.environ["SEARCH_PATH"])

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

# pylint: disable=too-few-public-methods
class Shape:
    """Shape object"""

    Caption = NamedTuple("Caption", [("en", str), ("zh", str)])
    Coordinates = NamedTuple("Coordinates", [("lat", float), ("long", float)])

    # pylint: disable=too-many-arguments
    def __init__(self, sort: int, filename: str, caption_en: str,
                 caption_zh: str, latitude: float, longitude: float) -> None:
        self.sort = int(sort)
        self.file = Path(SEARCH_PATH / filename).resolve(strict=True)
        self.caption = self.Caption(caption_en, caption_zh)
        self.geo = self.Coordinates(float(latitude), float(longitude))

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
    parser.add_argument("data", type=Path, metavar="TSV_FILE",
                        help="path to tab-delimited data file")
    args = parser.parse_args()

    LOG.debug("Using search path \"%s\"", SEARCH_PATH)
    SEARCH_PATH.resolve(strict=True)

    with args.data.open() as data_fd:
        data_reader = csv.DictReader(data_fd, delimiter="\t", dialect="unix")
        shapes = [Shape(**row) for row in data_reader]

    twitter = Twitter()

    shape = random.choice(shapes)
    tweet = twitter.update(shape)

    LOG.info("\"%s\" from %s", tweet.text, tweet.place.full_name)

    if tweet.geo["coordinates"] != [*shape.geo]:
        LOG.error("Coordinate mismatch! Sent %s, received %s",
                  shape.geo, tweet.geo["coordinates"])
        tweet.destroy()
        raise RuntimeError("Coordinate mismatch, tweet destroyed")

if __name__ == "__main__":
    main()
