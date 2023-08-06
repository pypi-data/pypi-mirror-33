
from ._obj_from_dict import ObjFromDict

from .request_rotb_curves import RequestRotbCurves
from .response_rotb_curves import ResponseRotbCurves

from .request_rotb_compute_strategy_components import RequestRotbComputeStrategyComponents
from .response_rotb_compute_strategy_components import ResponseRotbComputeStrategyComponents
from .slice_rotb_compute_strategy_components import SliceRotbComputeStrategyComponents
from .slice_rotb_compute_strategy_components_risk_analysis import SliceRotbComputeStrategyComponentsRiskAnalysis

from .request_rotb_compute_strategy import RequestRotbComputeStrategy
from .response_rotb_compute_strategy import ResponseRotbComputeStrategy
from .slice_rotb_compute_strategy import SliceRotbComputeStrategy
from .slice_rotb_compute_strategy_risk_analysis import SliceRotbComputeStrategyRiskAnalysis

from .request_rotb_compute_strategy_prices import RequestRotbComputeStrategyPrices
from .response_rotb_compute_strategy_prices import ResponseRotbComputeStrategyPrices
from .slice_rotb_compute_strategy_prices import SliceRotbComputeStrategyPrices
from .slice_rotb_compute_strategy_prices_risk_analysis import SliceRotbComputeStrategyPricesRiskAnalysis

dic_endpoint = {
    'v1_curves': {
        'request': RequestRotbCurves,
        'response': ResponseRotbCurves,
    },
    'v1_compute_strategy_components': {
        'request': RequestRotbComputeStrategyComponents,
        'response': ResponseRotbComputeStrategyComponents,
        'slice': SliceRotbComputeStrategyComponents,
        'slice_riskAnalysis': SliceRotbComputeStrategyComponentsRiskAnalysis
    },
    'v1_compute_strategy': {
        'request': RequestRotbComputeStrategy,
        'response': ResponseRotbComputeStrategy,
        'slice': SliceRotbComputeStrategy,
        'slice_riskAnalysis': SliceRotbComputeStrategyRiskAnalysis,
    },
    'v1_compute_strategy_prices': {
        'request': RequestRotbComputeStrategyPrices,
        'response': ResponseRotbComputeStrategyPrices,
        'slice': SliceRotbComputeStrategyPrices,
        'slice_riskAnalysis': SliceRotbComputeStrategyPricesRiskAnalysis,
    },
    # to add new endpoint here after creating the corresponding
    # Request Response and optionally Slice objects
}

endpoint = ObjFromDict(dic_endpoint)
