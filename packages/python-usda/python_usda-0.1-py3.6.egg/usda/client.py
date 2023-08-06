#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .enums import *
from .domain import Nutrient, Food, FoodReport
from .base import DataGovClientBase, get_response_data


class UsdaClient(DataGovClientBase):

    def __init__(self, api_gov_key):
        super(UsdaClient, self).__init__('usda/', api_gov_key)

    def list_nutrients(self, max, offset=0, sort='n'):
        uri = super(UsdaClient, self).build_uri(
            UsdaApis.ndb.value, UsdaUriActions.list.value,
            lt=UsdaNdbListType.all_nutrients.value, max=max,
            offset=offset, sort=sort)
        response_data = get_response_data(uri)
        nutrients = self._build_nutrients_list(response_data)
        return nutrients

    def list_foods(self, max, offset=0, sort='n'):
        uri = super(UsdaClient, self).build_uri(
            UsdaApis.ndb.value, UsdaUriActions.list.value,
            lt=UsdaNdbListType.food.value, max=max, offset=offset, sort=sort)
        response_data = get_response_data(uri)
        foods = self._build_foods_list(response_data)
        return foods

    def get_food_report(self, ndb_food_id,
                        report_type=UsdaNdbReportType.basic):
        uri = super(UsdaClient, self).build_uri(
            UsdaApis.ndb.value, UsdaUriActions.report.value,
            type=report_type.value, ndbno=ndb_food_id)
        response_data = get_response_data(uri)
        return FoodReport.from_response_data(response_data)

    def get_nutrient_report(self, ndb_nutrient_id,
                            report_type=UsdaNdbReportType.basic):
        uri = super(UsdaClient, self).build_uri(
            UsdaApis.ndb.value, UsdaUriActions.report.value,
            type=report_type.value, ndbno=ndb_nutrient_id)

    def _build_item_list(self, data, usda_class):
        result = list()
        data_list = data['list']['item']
        for raw_data in data_list:
            result.append(usda_class.from_response_data(raw_data))
        return result

    def _build_nutrients_list(self, response_data):
        return self._build_item_list(response_data, Nutrient)

    def _build_foods_list(self, response_data):
        return self._build_item_list(response_data, Food)

    def _build_food_report(self, response_data):
        return FoodReport(response_data)
