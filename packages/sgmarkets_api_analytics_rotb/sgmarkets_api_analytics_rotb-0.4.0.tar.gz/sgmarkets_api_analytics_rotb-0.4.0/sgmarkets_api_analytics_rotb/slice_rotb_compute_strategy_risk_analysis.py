# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 15:30:04 2018

@author: kferret061312
"""
from .response_rotb_compute_strategy_components import ResponseRotbComputeStrategyComponents
from .response_rotb_compute_strategy_prices import ResponseRotbComputeStrategyPrices
from .slice_rotb_compute_strategy_prices_risk_analysis import SliceRotbComputeStrategyPricesRiskAnalysis
from .slice_rotb_compute_strategy_components_risk_analysis import SliceRotbComputeStrategyComponentsRiskAnalysis


class SliceRotbComputeStrategyRiskAnalysis:
    """
    """

    def __init__(self,
                 obj_res,
                 x=None,
                 y=None,
                 z=None,
                 dic_req_fix=None,
                 value=None,
                 y_pos='index',  # index or column
                 ):
        assert isinstance(obj_res, ResponseRotbComputeStrategyComponents) or isinstance(obj_res, ResponseRotbComputeStrategyPrices), \
            'Error: obj_res must be a ResponseRotbComputeStrategyComponents object or ResponseRotbComputeStrategyPrices'
        if isinstance(obj_res, ResponseRotbComputeStrategyComponents):
            sli = SliceRotbComputeStrategyComponentsRiskAnalysis(
                obj_res,
                x,
                y,
                z,
                dic_req_fix,
                value,
                y_pos,  # index or column
            )
            self.df_pivot = sli.df_pivot
        else:
            sli = SliceRotbComputeStrategyPricesRiskAnalysis(
                obj_res,
                x,
                y,
                z,
                dic_req_fix,
                value,
                y_pos,  # index or column
            )
            self.df_pivot = sli.df_pivot
