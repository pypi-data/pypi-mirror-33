#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from usda.enums import \
    UsdaApis, UsdaNdbListType, UsdaNdbReportType, UsdaUriActions
from usda.domain import Nutrient, Food, FoodReport, NutrientReport
from usda.base import DataGovClientBase


class UsdaClient(DataGovClientBase):
    """Describes a USDA NDB API client."""

    def __init__(self, api_gov_key):
        """Create a USDA NDB API client.
        For small testing purposes, you may use `DEMO_KEY` as an API key ;
        but beware of rate limit errors."""
        super(UsdaClient, self).__init__('usda/', UsdaApis.ndb, api_gov_key)

    def list_nutrients(self, max, offset=0, sort='n'):
        """Get a list of available nutrients in the database.
        Useful to generate Nutrient Reports."""
        data = self.run_request(
            UsdaUriActions.list, lt=UsdaNdbListType.all_nutrients.value,
            max=max, offset=offset, sort=sort)
        return self._build_nutrients_list(data)

    def list_foods(self, max, offset=0, sort='n'):
        """Get a list of available food items in the database.
        Useful to generate Food Reports."""
        data = self.run_request(
            UsdaUriActions.list, lt=UsdaNdbListType.food.value,
            max=max, offset=offset, sort=sort)
        return self._build_foods_list(data)

    def get_food_report(self, ndb_food_id,
                        report_type=UsdaNdbReportType.basic):
        """Get a Food Report for a given food item ID."""
        data = self.run_request(
            UsdaUriActions.report, type=report_type.value, ndbno=ndb_food_id)
        return FoodReport.from_response_data(data)

    def get_nutrient_report(self, nutrients):
        """Get a Nutrient Report for each of the given nutrient IDs."""
        if len(nutrients) > 20:
            raise ValueError("A nutrient report request cannot contain "
                             "more than 20 nutrients")
        data = self.run_request(
            UsdaUriActions.nutrients, nutrients=nutrients)
        return NutrientReport.from_response_data(data)

    def _build_item_list(self, data, usda_class):
        """Generate a list of USDA objects from parsed JSON data."""
        result = list()
        data_list = data['list']['item']
        for raw_data in data_list:
            result.append(usda_class.from_response_data(raw_data))
        return result

    def _build_nutrients_list(self, response_data):
        """Generate a list of nutrients."""
        return self._build_item_list(response_data, Nutrient)

    def _build_foods_list(self, response_data):
        """Generate a list of food items."""
        return self._build_item_list(response_data, Food)
