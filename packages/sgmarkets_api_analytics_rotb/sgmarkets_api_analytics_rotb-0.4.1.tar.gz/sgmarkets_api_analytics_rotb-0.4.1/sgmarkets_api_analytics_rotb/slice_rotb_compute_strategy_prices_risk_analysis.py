# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 10:59:02 2018

@author: kferret061312
"""


import os
import copy
import functools

import datetime as dt
import pandas as pd

from IPython.display import Markdown
from dateutil.parser import parse

from ._util import Util
from .response_rotb_compute_strategy_prices import ResponseRotbComputeStrategyPrices
from sgmarkets_api_auth.util import save_result


class SliceRotbComputeStrategyPricesRiskAnalysis:
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
        """
        """
        # print(type(obj_res))
        assert isinstance(obj_res, ResponseRotbComputeStrategyPrices), \
            'Error: obj_res must be a ResponseRotbComputeStrategyPrices object'
        self.res = obj_res
        self.y_pos = y_pos

        msg1 = 'Error: {} must be a column name in df_res_ra'
        msg1b = 'Error: y_pos must be a "index" or "column"'
        msg2 = 'z must be None if y is None'
        msg3 = 'Error: dic_req_fix must be a dict'
        msg4 = 'Error: {} is not a column of df_req_ra'
        msg5 = 'Error: {} has {} values - Must be one'
        msg6 = 'Error: value must be a column of df_res_ra'
        msg7 = 'Error: {} is present in dic_req_fix'
        msg8 = 'Error: {} has {} values in dic_res_param - Must be one'

        assert x in self.res.df_res_ra.columns, msg1.format('x')
        if y:
            assert y in self.res.df_res_ra.columns, msg1.format('y')
            assert y_pos in ['index', 'column'], msg1b
        if x and y:
            if z is not None:
                assert z in self.res.df_res_ra.columns, msg1.format('z')
        else:
            assert z is None, msg2

        assert isinstance(dic_req_fix, dict), msg3
        assert value in self.res.df_res_ra.columns, msg4.format(value)

        li_xyz = [e for e in [x, y, z] if e is not None]
        if len(li_xyz) == 1:

            df_slice = obj_res.df_res_ra[[x, value]]
            df_pivot = df_slice.set_index([x], inplace=True)

        if len(li_xyz) == 2:
            # display(df_slice)
            df_pivot = obj_res.df_res_ra.pivot_table(index=x,
                                                     columns=y,
                                                     values=value)
            # display(df_pivot)

        if len(li_xyz) == 3:
            df_pivot = obj_res.df_res_ra[[x, y, z, value]]

            if self.y_pos == 'index':
                df_pivot = df_pivot.pivot_table(index=[x, y],
                                                columns=z,
                                                values=value)

                df_pivot = df_pivot.reindex(obj_res.df_res_ra[x].drop_duplicates(),
                                            axis=0,
                                            level=0)
                df_pivot = df_pivot.reindex(obj_res.df_res_ra[y].drop_duplicates(),
                                            axis=0,
                                            level=1)

                df_pivot = df_pivot.reindex(obj_res.df_res_ra[z].drop_duplicates(),
                                            axis=1)

            if self.y_pos == 'column':
                df_pivot = df_pivot.pivot_table(index=x,
                                                columns=[y, z],
                                                values=value)
                df_pivot = df_pivot.reindex(obj_res.df_res_ra[x].drop_duplicates(),
                                            axis=0)
                df_pivot = df_pivot.reindex(obj_res.df_res_ra[y].drop_duplicates(),
                                            axis=1,
                                            level=0)
                df_pivot = df_pivot.reindex(obj_res.df_res_ra[z].drop_duplicates(),
                                            axis=1,
                                            level=1)

        self.df_pivot = df_pivot
        # transform

    def save(self,
             folder_save='dump',
             name=None,
             tagged=True,
             excel=False):
        """
        """
        if name is None:
            name = 'SG_Research_ROTB'

        save_result(self.df_pivot,
                    folder_save, name=name + '_Prices_RA_response',
                    tagged=tagged,
                    excel=excel)

    def _repr_html_(self):
        """
        """
        return self.df_slice_ra.to_html()

    def info(self):
        """
        """
        md = """
A SliceRotbComputeStrategyComponents object has the following properties:
+ `df_slice`: dataframe extracted from the postprocess dataframe `df_set` so that:
    + No constraints on params `x`, `y` (if input), `z` (if input)
    + All other request params are kept only if their value match the `dic_req_fix` dictionary of fixed values
        + All request params not `x` or `y` or `z` having more than one value must be specified in `dic_req_fix`
    + Only the response param `value` is kept

+ `df_pivot`: dataframe extracted from `df_slice`. It can be of dimension:
+ 1 if only `x` is defined
+ 2 if `x`and `y` are defined
+ 3 if `x`and `y` and `z` are defined
    + If the dimension is 3 and `y_pos` is `index` then (`x`, `y`) are a dataframe row multi-index
    + If the dimension is 3 and `y_pos` is `column` then (`y`, `z`) are a dataframe column multi-index
        """
        return Markdown(md)
