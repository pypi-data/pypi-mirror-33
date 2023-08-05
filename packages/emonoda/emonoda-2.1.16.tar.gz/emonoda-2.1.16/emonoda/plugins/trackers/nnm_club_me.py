"""
    Emonoda -- A set of tools to organize and manage your torrents
    Copyright (C) 2015  Devaev Maxim <mdevaev@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import re

from typing import Dict
from typing import Any

from ...optconf import Option

from . import WithLogin
from . import WithCheckScrape
from . import WithFetchByDownloadId
from . import WithStat


# =====
class Plugin(WithLogin, WithCheckScrape, WithFetchByDownloadId, WithStat):
    PLUGIN_NAMES = [
        "nnm-club.me",
        "nnm-club.name",
        "nnmclub.to",
    ]

    _NNM_DOMAIN = PLUGIN_NAMES[0]

    _SITE_VERSION = 4
    _SITE_ENCODING = "cp1251"

    _SITE_FINGERPRINT_URL = "https://{}".format(_NNM_DOMAIN)
    _SITE_FINGERPRINT_TEXT = "<link rel=\"canonical\" href=\"http://{}/\">".format(_NNM_DOMAIN)

    _COMMENT_REGEXP = re.compile(r"https?://(nnm-club\.(me|ru|name|tv|lib)|nnmclub\.to)"
                                 r"/forum/viewtopic\.php\?p=(?P<torrent_id>\d+)")

    _TORRENT_SCRAPE_URL = "http://bt.{}:2710/scrape.php?info_hash={{scrape_hash}}".format(_NNM_DOMAIN)

    _DOWNLOAD_ID_URL = "https://{}/forum/viewtopic.php?p={{torrent_id}}".format(_NNM_DOMAIN)
    _DOWNLOAD_ID_REGEXP = re.compile(r"filelst.php\?attach_id=(?P<download_id>[a-zA-Z0-9]+)")
    _DOWNLOAD_URL = "https://{}//forum/download.php?id={{download_id}}".format(_NNM_DOMAIN)

    _STAT_URL = _DOWNLOAD_ID_URL
    _STAT_OK_REGEXP = _DOWNLOAD_ID_REGEXP
    _STAT_SEEDERS_REGEXP = re.compile(r"align=\"center\"><span class=\"seed\">\[\s+<b>(?P<seeders>\d+)")
    _STAT_LEECHERS_REGEXP = re.compile(r"align=\"center\"><span class=\"leech\">\[\s+<b>(?P<leechers>\d+)")

    def __init__(self, **kwargs: Any) -> None:  # pylint: disable=super-init-not-called
        self._init_bases(**kwargs)
        self._init_opener(with_cookies=True)

    @classmethod
    def get_options(cls) -> Dict[str, Option]:
        return cls._get_merged_options({
            "timeout": Option(default=20.0, help="Timeout for HTTP client"),
        })

    # ===

    def login(self) -> None:
        self._login_using_post(
            url="https://{}/forum/login.php".format(self._NNM_DOMAIN),
            post={
                "username": self._encode(self._user),
                "password": self._encode(self._passwd),
                "redirect": b"",
                "login":    b"\xc2\xf5\xee\xe4",
            },
            ok_text="class=\"mainmenu\">Выход [ {} ]</a>".format(self._user),
        )
