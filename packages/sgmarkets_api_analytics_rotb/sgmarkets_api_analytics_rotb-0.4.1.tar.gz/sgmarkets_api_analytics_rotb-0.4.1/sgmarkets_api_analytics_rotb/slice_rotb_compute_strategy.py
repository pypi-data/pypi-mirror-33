
from copy import deepcopy

import datetime as dt
import pandas as pd

from sgmarkets_api_auth.util import save_result


class SliceRotbComputeStrategy():
    """
    TBU
    """

    def __init__(self,
                 obj_res,
                 x=None,
                 y=None,
                 z=None,
                 dic_req_fix={},
                 value=None,
                 y_pos='index',  # index or column
                 other_pos='column'):
        """
        """

        msg1 = 'Error: {} must be a column name in components.df_set'
        msg2 = 'Error: {} must be a value in column {} of components.df_set'
        msg3 = 'Error: y must not be None. x and z could.'

        obj = obj_res
        obj.df_res = obj.df_set.copy(deep=True)

        for k, v in iter(dic_req_fix.items()):
            if not isinstance(v, list):
                v = [v]

            assert k in obj.df_set.columns, msg1.format(k)
            if k is 'date':
                if 'range' in v:
                    v.remove('range')
                    mask = (obj.df_set[k] >= v[0]) & (obj.df_set[k] <= v[1])
                    obj.df_res = obj.df_res.loc[mask]
                else:
                    mask = (obj.df_set[k] == v[0]) & (obj.df_set[k] == v[1])
                    obj.df_res = obj.df_set.loc[mask]
            else:
                assert v[0] in obj.df_set[k].values, msg2.format(v[0], k)
                mask = (obj.df_set[k] == v[0])

                if len(v) > 1:
                    v.remove(v[0])
                    for v_ in v:
                        assert v_ in obj.df_set[k], msg2.format(v_, k)
                        mask = mask | (obj.df_set[k] == v_)
                obj.df_res = obj.df_set.loc[mask]

        self.df_slice = deepcopy(obj.df_res)

        if not isinstance(value, list):
            value = [value]

        assert y is not None, msg3

        li_xyz = [e for e in [x, y, z] if e is not None]

        if len(li_xyz) is 1:
            li_xz = []
        else:
            li_xz = deepcopy(li_xyz)
            li_xz.remove(y)

        values = value + li_xyz + list(dic_req_fix.keys())

        self.df_pivot = None
        tmp = self.df_slice[values]
        indexer = list(dic_req_fix.keys()) + li_xz
        if y_pos.lower() == 'index':
            if other_pos.lower() == 'column':
                self.df_pivot = tmp.pivot_table(value, index=y, columns=indexer)
            elif other_pos.lower() == 'index':
                self.df_pivot = tmp.set_index(indexer + [y] + value)
            else:
                raise Exception
        elif y_pos.lower() == 'column':
            if other_pos.lower() == 'column':
                self.df_pivot = tmp.set_index(indexer + [y] + value).T
            elif other_pos.lower() == 'index':
                self.df_pivot = tmp.pivot_table(value, index=indexer, columns=y)
            else:
                raise Exception
        else:
            raise Exception

        self.df_pivot = self.df_pivot.dropna()

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
                    folder_save,
                    name=name + '_Components_Slice',
                    tagged=tagged,
                    excel=excel)
