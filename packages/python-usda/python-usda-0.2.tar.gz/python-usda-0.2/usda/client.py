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

    def list_nutrients_raw(self, **kwargs):
        """
        Get a list of available nutrients in the database as JSON.
        """
        kwargs.setdefault('lt', UsdaNdbListType.all_nutrients.value)
        return self.run_request(UsdaUriActions.list, **kwargs)

    def list_nutrients(self, max, offset=0, sort='n'):
        """
        Get a list of available nutrients in the database.
        Useful to generate Nutrient Reports.
        """
        return self._build_nutrients_list(
            self.list_nutrients_raw(max=max, offset=offset, sort=sort)
        )

    def list_foods_raw(self, **kwargs):
        """
        Get a list of available food items in the database as JSON.
        """
        kwargs.setdefault('lt', UsdaNdbListType.food.value)
        return self.run_request(UsdaUriActions.list, **kwargs)

    def list_foods(self, max, offset=0, sort='n'):
        """
        Get a list of available food items in the database.
        Useful to generate Food Reports.
        """
        return self._build_foods_list(
            self.list_foods_raw(max=max, offset=offset, sort=sort)
        )

    def search_foods_raw(self, **kwargs):
        """
        Get a list of food items matching a specified query, as JSON.
        """
        return self.run_request(UsdaUriActions.search, **kwargs)

    def search_foods(self, query, max, offset=0, sort='r'):
        """
        Get a list of food items matching a specified query.
        """
        return self._build_foods_list(
            self.search_foods_raw(q=query, max=max, offset=offset, sort=sort))

    def get_food_report_raw(self, **kwargs):
        """
        Get a Food Report for a given food item ID as JSON.
        """
        return self.run_request(UsdaUriActions.report, **kwargs)

    def get_food_report(self, ndb_food_id,
                        report_type=UsdaNdbReportType.basic):
        """
        Get a Food Report for a given food item ID.
        """
        return FoodReport.from_response_data(
            self.get_food_report_raw(type=report_type.value, ndbno=ndb_food_id)
        )

    def get_nutrient_report_raw(self, **kwargs):
        """
        Get a Nutrient Report for each of the given nutrient IDs as JSON.
        """
        return self.run_request(UsdaUriActions.nutrients, **kwargs)

    def get_nutrient_report(self, nutrients):
        """
        Get a Nutrient Report for each of the given nutrient IDs.
        """
        if len(nutrients) > 20:
            raise ValueError("A nutrient report request cannot contain "
                             "more than 20 nutrients")
        return NutrientReport.from_response_data(
            self.get_nutrient_report_raw(nutrients=nutrients)
        )

    def _build_item_list(self, data, usda_class):
        """
        Generate a list of USDA objects from parsed JSON data.
        """
        return list(map(usda_class.from_response_data, data['list']['item']))

    def _build_nutrients_list(self, response_data):
        """
        Generate a list of nutrients.
        """
        return self._build_item_list(response_data, Nutrient)

    def _build_foods_list(self, response_data):
        """
        Generate a list of food items.
        """
        return self._build_item_list(response_data, Food)
