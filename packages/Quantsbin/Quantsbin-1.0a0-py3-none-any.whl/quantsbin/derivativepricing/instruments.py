"""
    developed by Quantsbin - Jun'18

"""

from abc import ABCMeta, abstractmethod
from datetime import datetime

from .engineconfig import PricingEngine
from .namesnmapper import VanillaOptionType, ExpiryType, DEFAULT_MODEL, UdlType, OBJECT_MODEL, DerivativeType


class Instrument(metaclass=ABCMeta):
    """
    Instrument - Metaclass to define financial instrument

    @abstract functions:
        payoff => defines payoff on instrument.
        engine => attach the instrument with the pricing model and market data.
    """

    @abstractmethod
    def payoff(self):
        pass

    def engine(self, **kwargs):
        """
        Binds pricing model class and market data to the object
            Args required:
                model: pricing model (default value set to BSM for European expiry)
                **kwargs: Dictionary of parameters and their corresponding value required for valuation.
                For arguments required and method available for each model check\
                help(.derivativepricing.pricingmodels.<model name>)
        """
        if not kwargs['model']:
            kwargs['model'] = DEFAULT_MODEL[self.undl][self.derivative_type][self.expiry_type]
        return PricingEngine(self, **kwargs)

    def list_models(self):
        return ", ".join(OBJECT_MODEL[self.undl][self.expiry_type])


class VanillaOption(Instrument):
    """
    Parent class for all Vanilla options on different underlying.

    Methods:
        payoff(spot0) ->
            Calculates the payoff of the function

        engine(model, **kwargs)
            Binds the inout parameter with pricing models.
            To check valid models for underlying use .models()
    """

    def __init__(self, option_type, expiry_type, strike, expiry_date, derivative_type):
        self.option_type = option_type or VanillaOptionType.CALL.value
        self.expiry_type = expiry_type or ExpiryType.EUROPEAN.value
        self.strike = strike
        self.expiry_date = datetime.strptime(expiry_date, '%Y%m%d')
        self.derivative_type = derivative_type or DerivativeType.VANILLA_OPTION.value

    @property
    def _option_type_flag(self):
        if self.option_type == VanillaOptionType.CALL.value:
            return 1
        else:
            return -1

    def payoff(self, spot0=None):
        """
        Calculates the payoff of option

         Defines payoff of the option
             Payoff(Call) = max(S-K,0)
             Payoff(Put) = max(K-S,0)
         Args required:
             spot0: Value of underlying e.g. 110
        """
        return max(self._option_type_flag * (spot0 - self.strike), 0.0)


class EqOption(VanillaOption):
    """
    Defines object for vanilla options on equity with both European and American expiry type.

    Args required:
            option_type: 'Call' or 'Put' (default value is set to 'Call')
            expiry_type: 'European' or 'American' (default is set to 'European')
            strike: (Float in same unit as underlying price) e.g. 110.0
            expiry_date: (Date in string format "YYYYMMDD") e.g. 10 Dec 2018 as "20181210"
            derivative_type: Default value as "Vanilla Option".
    """

    def __init__(self, option_type=VanillaOptionType.CALL.value, expiry_type=ExpiryType.EUROPEAN.value,
                 strike=None, expiry_date=None, derivative_type=None
                 ):
        super().__init__(option_type, expiry_type, strike, expiry_date, derivative_type)
        self.undl = UdlType.STOCK.value

    def engine(self, model=None, spot0=None, rf_rate=0, yield_div=0, div_list=None, volatility=None,
               pricing_date=None, **kwargs):
        return super().engine(model=model, spot0=spot0, rf_rate=rf_rate, cnv_yield=yield_div, pv_cnv=0,
                              div_list=div_list, volatility=volatility, pricing_date=pricing_date, **kwargs)


class FutOption(VanillaOption):
    """
    Defines object for vanilla options on futures with both European and American expiry type.

    Args required:
            option_type: 'Call' or 'Put' (default value is set to 'Call')
            expiry_type: 'European' or 'American' (default is set to 'European')
            strike: (Float in same unit as underlying price) e.g. 110.0
            expiry_date: (Date in string format "YYYYMMDD") e.g. 10 Dec 2018 as "20181210".
    """

    def __init__(self, option_type=VanillaOptionType.CALL.value, expiry_type=ExpiryType.EUROPEAN.value,
                 strike=None, expiry_date=None, derivative_type=None
                 ):
        super().__init__(option_type, expiry_type, strike, expiry_date, derivative_type)
        self.undl = UdlType.FUTURES.value

    def engine(self, model=None, fwd0=None, rf_rate=0, volatility=None, pricing_date=None, **kwargs):
        return super().engine(model=model, spot0=fwd0, rf_rate=rf_rate, cnv_yield=rf_rate,
                              volatility=volatility, pricing_date=pricing_date, **kwargs)


class FXOption(VanillaOption):
    """
    Defines object for vanilla options on fx rates with both European and American expiry type.

    Args required:
            option_type: 'Call' or 'Put' (default value is set to 'Call')
            expiry_type: 'European' or 'American' (default is set to 'European')
            strike: (Float in same unit as underlying price) e.g. 110.0
            expiry_date: (Date in string format "YYYYMMDD") e.g. 10 Dec 2018 as "20181210".
    """

    def __init__(self, option_type=VanillaOptionType.CALL.value, expiry_type=ExpiryType.EUROPEAN.value,
                 strike=None, expiry_date=None, derivative_type=None
                 ):
        super().__init__(option_type, expiry_type, strike, expiry_date, derivative_type)
        self.undl = UdlType.FX.value

    def engine(self, model=None, spot0=None, rf_rate_local=0, rf_rate_foreign=0, volatility=None,
               pricing_date=None, **kwargs):
        return super().engine(model=model, spot0=spot0, rf_rate_local=rf_rate_local, rf_rate_foreign=rf_rate_foreign,
                              volatility=volatility, pricing_date=pricing_date, **kwargs)


class ComOption(VanillaOption):
    """
    Defines object for vanilla options on commodities with both European and American expiry type.

    Args required:
            option_type: 'Call' or 'Put' (default value is set to 'Call')
            expiry_type: 'European' or 'American' (default is set to 'European')
            strike: (Float in same unit as underlying price) e.g. 110.0
            expiry_date: (Date in string format "YYYYMMDD") e.g. 10 Dec 2018 as "20181210".
    """
    def __init__(self, option_type=VanillaOptionType.CALL.value, expiry_type=ExpiryType.EUROPEAN.value,
                 strike=None, expiry_date=None, derivative_type=None
                 ):
        super().__init__(option_type, expiry_type, strike, expiry_date, derivative_type)
        self.undl = UdlType.COMMODITY.value

    def engine(self, model=None, spot0=None, rf_rate=0, cnv_yield=0, cost_yield=0, volatility=None,
               pricing_date=None, **kwargs):
        return super().engine(model=model, spot0=spot0, rf_rate=rf_rate, cnv_yield=cnv_yield, cost_yield=cost_yield,
                              volatility=volatility, pricing_date=pricing_date, **kwargs)
