#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from usda.enums import \
    UsdaApis, UsdaNdbListType, UsdaNdbReportType, UsdaUriActions
from usda.domain import \
    ListItem, Nutrient, Food, FoodReport, FoodReportV2, NutrientReportFood
from usda.base import DataGovClientBase, DataGovApiError
from usda.pagination import \
    RawPaginator, ModelPaginator, RawNutrientReportPaginator


class UsdaClient(DataGovClientBase):
    """Describes a USDA NDB API client."""

    def __init__(self, api_gov_key):
        """Create a USDA NDB API client.
        For small testing purposes, you may use `DEMO_KEY` as an API key ;
        but beware of rate limit errors."""
        super().__init__('usda/', UsdaApis.ndb, api_gov_key)

    def list_nutrients_raw(self, **kwargs):
        """
        Get a list of available nutrients in the database as JSON.
        """
        kwargs.setdefault('lt', UsdaNdbListType.all_nutrients.value)
        return RawPaginator(self, UsdaUriActions.list, **kwargs)

    def list_nutrients(self, max, offset=0, sort='n'):
        """
        Get a list of available nutrients in the database.
        Useful to generate Nutrient Reports.
        """
        return ModelPaginator(
            Nutrient,
            self.list_nutrients_raw(max=max, offset=offset, sort=sort),
        )

    def list_foods_raw(self, **kwargs):
        """
        Get a list of available food items in the database as JSON.
        """
        kwargs.setdefault('lt', UsdaNdbListType.food.value)
        return RawPaginator(self, UsdaUriActions.list, **kwargs)

    def list_foods(self, max, offset=0, sort='n'):
        """
        Get a list of available food items in the database.
        Useful to generate Food Reports.
        """
        return ModelPaginator(
            Food,
            self.list_foods_raw(max=max, offset=offset, sort=sort),
        )

    def list_food_groups_raw(self, **kwargs):
        """
        Get a list of available food groups in the database as JSON.
        """
        kwargs.setdefault('lt', UsdaNdbListType.food_groups.value)
        return RawPaginator(self, UsdaUriActions.list, **kwargs)

    def list_food_groups(self, max, offset=0, sort='n'):
        """
        Get a list of available food groups in the database.
        """
        return ModelPaginator(
            ListItem,
            self.list_food_groups_raw(max=max, offset=offset, sort=sort),
        )

    def list_derivation_codes_raw(self, **kwargs):
        """
        Get a list of available derivation codes in the database as JSON.
        """
        kwargs.setdefault('lt', UsdaNdbListType.derivation_codes.value)
        return RawPaginator(self, UsdaUriActions.list, **kwargs)

    def list_derivation_codes(self, max, offset=0, sort='n'):
        """
        Get a list of available derivation codes in the database.
        """
        return ModelPaginator(
            ListItem,
            self.list_derivation_codes_raw(max=max, offset=offset, sort=sort),
        )

    def search_foods_raw(self, **kwargs):
        """
        Get a list of food items matching a specified query, as JSON.
        """
        return RawPaginator(self, UsdaUriActions.search, **kwargs)

    def search_foods(self, query, max, offset=0, sort='r'):
        """
        Get a list of food items matching a specified query.
        """
        return ModelPaginator(
            Food,
            self.search_foods_raw(q=query, max=max, offset=offset, sort=sort),
        )

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

    def get_food_report_v2_raw(self, **kwargs):
        """
        Get a Food Report version 2 for one or more food item IDs as JSON.
        """
        return self.run_request(UsdaUriActions.v2report, **kwargs)

    def get_food_report_v2(self, *ids, report_type=UsdaNdbReportType.basic):
        """
        Get a list of Food Reports version 2 for one or more food item IDs.
        """
        def _get_report(food):
            if 'error' in food:
                raise DataGovApiError(food['error'])
            return FoodReportV2.from_response_data(food)

        return list(map(
            _get_report,
            self.get_food_report_v2_raw(
                type=report_type.value, ndbno=ids,
            )['foods']
        ))

    def get_nutrient_report_raw(self, **kwargs):
        """
        Get a Nutrient Report for each of the given nutrient IDs as JSON.
        """
        return RawNutrientReportPaginator(
            self, UsdaUriActions.nutrients, **kwargs)

    def get_nutrient_report(self, *nutrients):
        """
        Get a Nutrient Report for each of the given nutrient IDs.
        """
        if len(nutrients) > 20:
            raise ValueError("A nutrient report request cannot contain "
                             "more than 20 nutrients")
        return ModelPaginator(
            NutrientReportFood,
            self.get_nutrient_report_raw(nutrients=nutrients),
        )
