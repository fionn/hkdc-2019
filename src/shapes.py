#!/usr/bin/env python3
"""Geographical shapes"""

import os
import csv
import random
import argparse
from pathlib import Path
from typing import NamedTuple

import tweepy

class Shape: # pylint: disable=too-few-public-methods
    """Shape object"""

    Caption = NamedTuple("Caption", [("en", str), ("zh", str)])
    Coordinates = NamedTuple("Coordinates", [("lat", float), ("long", float)])

    # pylint: disable=too-many-arguments
    def __init__(self, sort: int, filename: str, caption_en: str,
                 caption_zh: str, latitude: float, longitude: float) -> None:
        self.sort = sort
        search_path = Path("assets/").resolve(strict=True)
        self.file = Path(search_path / filename).resolve(strict=True)
        self.caption = self.Caption(caption_en, caption_zh)
        self.geo = self.Coordinates(latitude, longitude)

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
    def compose(shape: Shape) -> dict:
        """Very over-egged, but want it to be generic for lat, long, etc."""
        status = f"{shape.caption.en}\n{shape.caption.zh}"
        return {"status": status, "lat": shape.geo.lat, "long": shape.geo.long}

    def update(self, shape: Shape) -> tweepy.Status:
        """Post tweet for shape"""
        #composition = self.compose(shape)
        #media = self.api.media_upload(filename=shape.file.name,
        #                              file=shape.file)
        #api.create_media_metadata(media.media_id, f"{shape.caption.en}")
        #return self.api.update(**composition, media_ids=[media.media_id])

def main() -> None:
    """Entry point"""
    parser = argparse.ArgumentParser(prog="shapes", description="Tweet shapes")
    parser.add_argument("data", type=Path,
                        help="path to TSV data file")
    args = parser.parse_args()

    with args.data.open() as data_fd:
        data_reader = csv.DictReader(data_fd, delimiter="\t", dialect="unix")
        shapes = [Shape(**row) for row in data_reader]

    twitter = Twitter()

    shape = random.choice(shapes)
    twitter.update(shape)

if __name__ == "__main__":
    main()
