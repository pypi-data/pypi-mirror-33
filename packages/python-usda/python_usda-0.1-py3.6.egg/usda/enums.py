#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum


class UsdaApis(Enum):
    ndb = "ndb"


class UsdaUriActions(Enum):
    list = "list"
    report = "reports"


class UsdaNdbListType(Enum):
    all_nutrients = "n"
    specialty_nutrients = "ns"
    standard_release_nutrients = "nr"
    food = "f"
    food_group = "g"


class UsdaNdbReportType(Enum):
    basic = "b"
    full = "f"
    stats = "s"
