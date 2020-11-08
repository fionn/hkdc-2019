#!/usr/bin/env python3
"""Hong Kong District Council constituencies"""

import os
import csv
import enum
import random
import logging
import argparse
from pathlib import Path
from typing import NamedTuple, Union

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
    nonpartisan = 3

    @classmethod
    def map(cls, identifier: str) -> "Faction":
        """Map identifiers to enumerations"""
        try:
            return cls[identifier]
        except KeyError as ex:
            raise ValueError(f"Can't enumerate {identifier}") from ex

# pylint: disable=too-few-public-methods,too-many-instance-attributes
class Constituency:
    """Constituency object"""

    Caption = NamedTuple("Caption", [("en", str), ("zh", str)])
    Coordinates = NamedTuple("Coordinates", [("lat", float), ("long", float)])

    # pylint: disable=too-many-arguments
    def __init__(self, sort: Union[int, str], filename: str,
                 caption_en: str, caption_zh: str,
                 latitude: Union[str, float], longitude: Union[str, float],
                 electoral_code: str, dc_winner: str,
                 percentage_democracy: Union[str, float]) -> None:
        self._search_path = Path(os.environ["SEARCH_PATH"])
        self.sort = int(sort)
        self.file = Path(self._search_path / filename).resolve(strict=True)
        self.caption = self.Caption(caption_en, caption_zh)
        self.geo = self.Coordinates(float(latitude), float(longitude))
        self.electoral_code = electoral_code
        self.dc_winner = Faction.map(dc_winner)
        self.percentage_democracy = percentage_democracy

    def __repr__(self) -> str:
        return f"Constituency{self.electoral_code, *self.caption, *self.geo}"

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
    def _compose(constituency: Constituency) -> dict:
        """Compose a status dictionary compatible with api.status_update"""
        if constituency.dc_winner == Faction.nonpartisan:
            affiliation = "non-partisan"
        else:
            affiliation = f"pro-{constituency.dc_winner.name}"

        text = f"{constituency.electoral_code}: " \
               f"{constituency.caption.en}, {constituency.caption.zh}.\n" \
               f"Voted {affiliation} in the 2019 District Council elections."
        return {"status": text,
                "lat": constituency.geo.lat,
                "long": constituency.geo.long}

    def update(self, constituency: Constituency, dry_run: bool = False) -> tweepy.Status:
        """Post tweet for constituency"""
        composition = self._compose(constituency)
        LOG.info("Selecting %s, %s, %s",
                 constituency.electoral_code,
                 constituency.caption.en,
                 constituency.caption.zh)

        if dry_run:
            return tweepy.Status

        with constituency.file.open("rb") as constituency_fd:
            media = self.api.media_upload(filename=constituency.file.name,
                                          file=constituency_fd)

        # Add metadata to images
        #self.api.create_media_metadata(media.media_id, constituency.caption.en)

        return self.api.update_status(**composition, media_ids=[media.media_id])

def main() -> None:
    """Entry point"""
    parser = argparse.ArgumentParser(description="Tweet HKDC constituencies")
    parser.add_argument("data", type=Path, metavar="CSV_FILE",
                        help="path to CSV data file")
    parser.add_argument("-n", "--dry-run", action="store_true")
    args = parser.parse_args()

    with args.data.open() as data_fd:
        data_reader = csv.DictReader(data_fd, delimiter=",", dialect="unix")
        constituencies = [Constituency(**row) for row in data_reader]

    twitter = Twitter()

    constituency = random.choice(constituencies)
    tweet = twitter.update(constituency, args.dry_run)

    try:
        LOG.info("\"%s\" from %s", tweet.text, tweet.place.full_name)
    except AttributeError:
        if not args.dry_run:
            raise

if __name__ == "__main__":
    main()
