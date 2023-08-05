# -*- coding: utf-8 -*-

# Copyright 2016-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://rule34.xxx/"""

from . import booru


class Rule34Extractor(booru.XmlParserMixin,
                      booru.GelbooruPageMixin,
                      booru.BooruExtractor):
    """Base class for rule34 extractors"""
    category = "rule34"
    api_url = "https://rule34.xxx/index.php"
    page_limit = 4000

    def __init__(self, match):
        super().__init__(match)
        self.params.update({"page": "dapi", "s": "post", "q": "index"})


class Rule34TagExtractor(booru.TagMixin, Rule34Extractor):
    """Extractor for images from rule34.xxx based on search-tags"""
    pattern = [(r"(?:https?://)?(?:www\.)?rule34\.xxx/(?:index\.php)?"
                r"\?page=post&s=list&tags=(?P<tags>[^&#]+)")]
    test = [("http://rule34.xxx/index.php?page=post&s=list&tags=danraku", {
        "content": "a01768c6f86f32eb7ebbdeb87c30b0d9968d7f97",
        "pattern": r"https?://(.?img\.)?rule34\.xxx/images/\d+/[0-9a-f]+\.jpg",
        "count": 2,
    })]


class Rule34PostExtractor(booru.PostMixin, Rule34Extractor):
    """Extractor for single images from rule34.xxx"""
    pattern = [(r"(?:https?://)?(?:www\.)?rule34\.xxx/(?:index\.php)?"
                r"\?page=post&s=view&id=(?P<post>\d+)")]
    test = [("http://rule34.xxx/index.php?page=post&s=view&id=1974854", {
        "content": "fd2820df78fb937532da0a46f7af6cefc4dc94be",
    })]
