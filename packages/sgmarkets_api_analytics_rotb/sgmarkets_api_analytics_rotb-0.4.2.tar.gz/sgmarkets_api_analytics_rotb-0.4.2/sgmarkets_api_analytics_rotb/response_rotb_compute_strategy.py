

from IPython.display import Markdown

from .response_rotb_compute_strategy_components import ResponseRotbComputeStrategyComponents
from .response_rotb_compute_strategy_prices import ResponseRotbComputeStrategyPrices

from sgmarkets_api_auth.util import save_result


class ResponseRotbComputeStrategy:
    """
    TBU
    """

    def __init__(self,
                 li_raw_data=None,
                 obj_req=None):
        """
        """
        assert isinstance(li_raw_data, list), \
            'Error: li_raw_data must be a list - Run call_api() again with debug=True'
        for dic_res in li_raw_data:
            assert isinstance(dic_res, dict), \
                'Error: Each dic_res must be a list - Run call_api() again with debug=True'
            assert 'componentSeries' in dic_res, \
                'Error: componentSeries must be a key of each dic_res - Run call_api() again with debug=True'
            assert 'strategySerie' in dic_res, \
                'Error: stratedySerie must be a key of each dic_res - Run call_api() again with debug=True'

        self.components = ResponseRotbComputeStrategyComponents(li_raw_data, obj_req)
        self.strategy = ResponseRotbComputeStrategyPrices(li_raw_data, obj_req)

    def save(self,
             folder_save='dump',
             name=None,
             tagged=True,
             excel=False):
        """
        Split save for strategyprice type since no df.set in the object
        """
        if name is None:
            name = 'SG_Research_ROTB'

        save_result(self.components.df_set,
                    folder_save,
                    name=name + 'Components',
                    tagged=tagged,
                    excel=excel)

        save_result(self.strategy.df_res,
                    folder_save,
                    name=name + 'Strategy_res',
                    tagged=tagged,
                    excel=excel)

        save_result(self.strategy.df_req,
                    folder_save,
                    name=name + 'Strategy_req',
                    tagged=tagged,
                    excel=excel)

    def info(self):
        """
        """
        md = """
A PostprocessROTB object from ComputeStrategy endpoint has the properties:
    
+ Contains two sub-objects:
    +   `.components` : object of class computestrategycomponent   
    +    `.strategy`: object of class computestrategyprice
+ Common properties:
    + `df_req`: request data (dataframe)
    + `df_res`: response data (dataframe)
    + `dic_req_param`: params in request, each param contains a list of all values taken (dictionary)
    + `dic_res_param`: params in response, each param contains a list of all values taken (dictionary)
    + `raw_data`: raw data in response under key 'componentSeries' (dictionary)
+ Additional properties for .components sub-object:    
    + `df_set`: request and response data combined (dataframe)

and the methods:
+ `save()` to save the data as `.csv` and `.xlsx` files
        """
        return Markdown(md)
