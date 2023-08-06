# -*- coding: utf-8 -*-

__author__ = "gao"

from abc import ABCMeta, abstractmethod

from AmazingQuant.utils import data_transfer, generate_random_id
from AmazingQuant.constant import RunMode, Period, RightsAdjustment, SlippageType, StockType, RecordDataType
from AmazingQuant.data_object import *
from AmazingQuant.analysis_center.event_analysis_engine import run_backtesting_analysis_engine
from .event_bar_engine import *


class StrategyBase(metaclass=ABCMeta):
    def __init__(self):
        self._run_mode = RunMode.BACKTESTING.value
        self._account = []
        self._capital = 1000000
        self._start = "2017-01-01"
        self._end = "2018-01-02"
        self._benchmark = "000300.SH"
        self._period = Period.DAILY.value  # 后续支持1min 3min 5min 等多周期
        self._universe = []
        self._rights_adjustment = RightsAdjustment.NONE.value
        self._timetag = 0
        # 数据缓存开关
        self._daily_data_cache = False
        self._one_min_data_cache = False
        # 取数据
        self._get_data = GetData()
        self.bar_index = 0

    @property
    def run_mode(self):
        return self._run_mode

    @run_mode.setter
    def run_mode(self, value):
        self._run_mode = value

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        self._account = value

    @property
    def capital(self):
        return self._capital

    @capital.setter
    def capital(self, value):
        self._capital = value

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        self._start = value

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        self._end = value

    @property
    def benchmark(self):
        return self._benchmark

    @benchmark.setter
    def benchmark(self, value):
        self._benchmark = value

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, value):
        self._period = value

    @property
    def universe(self):
        return self._universe

    @universe.setter
    def universe(self, value):
        self._universe.extend(value)

    @property
    def rights_adjustment(self):
        return self._rights_adjustment

    @rights_adjustment.setter
    def rights_adjustment(self, value):
        self._rights_adjustment = value

    @property
    def timetag(self):
        return self._timetag

    @timetag.setter
    def timetag(self, value):
        self._timetag = value

    @property
    def daily_data_cache(self):
        return self._daily_data_cache

    @daily_data_cache.setter
    def daily_data_cache(self, value):
        self._daily_data_cache = value

    @property
    def one_min_data_cache(self):
        return self._one_min_data_cache

    @one_min_data_cache.setter
    def one_min_data_cache(self, value):
        self._one_min_data_cache = value

    # 回测滑点设置
    def set_slippage(self, stock_type=StockType.STOCK.value, slippage_type=SlippageType.SLIPPAGE_FIX.value, value=0):
        Environment.slippage_dict[stock_type] = {"slippage_type": slippage_type, "value": value}

    # 回测手续费和印花税
    def set_commission(self, stock_type=StockType.STOCK.value, tax=0, open_commission=0, close_commission=0,
                       close_today_commission=0, min_commission=0):
        Environment.commission_dict[stock_type] = {"tax": tax, "open_commission": open_commission,
                                                   "close_commission": close_commission,
                                                   "close_today_commission": close_today_commission,
                                                   "min_commission": min_commission}

    def run(self, save_trade_record=False):
        self.initialize()

        # 初始化　account_data
        if self.account:
            for account in self.account:
                Environment.current_account_data = AccountData()
                Environment.current_account_data.account_id = generate_random_id.generate_random_id(account)
                Environment.current_account_data.total_balance = self.capital[account]
                Environment.current_account_data.available = self.capital[account]
                Environment.bar_account_data_list.append(Environment.current_account_data)

        if self.run_mode == RunMode.TRADE.value:
            self.end = self._get_data.get_end_timetag(benchmark=self.benchmark, period=Period.DAILY.value)

        # 缓存数据开关，和bar_index的计算
        if self.period == Period.DAILY.value:
            self.daily_data_cache = True
        elif self.period == Period.ONE_MIN.value:
            self.one_min_data_cache = True
        stock_list = copy.copy(self.universe)
        stock_list.append(self.benchmark)
        stock_list = list(set(stock_list))
        if self._daily_data_cache:
            Environment.daily_data = self._get_data.get_all_market_data(stock_code=stock_list,
                                                                        field=["open", "high", "low", "close",
                                                                               "volumn", "amount"],
                                                                        end=self.end, period=Period.DAILY.value)
        if self.one_min_data_cache:
            Environment.one_min_data = self._get_data.get_all_market_data(stock_code=stock_list,
                                                                          field=["open", "high", "low", "close",
                                                                                 "volumn", "amount"],
                                                                          end=self.end, period=Period.ONE_MIN.value)

        if self.period == Period.DAILY.value:
            Environment.benchmark_index = [data_transfer.date_to_millisecond(str(int(i)), '%Y%m%d') for i in
                                           Environment.daily_data["open"].ix[self.benchmark].index
                                           if i >= data_transfer.date_str_to_int(self.start)]

        elif self.period == Period.ONE_MIN.value:
            Environment.benchmark_index = [data_transfer.date_to_millisecond(str(int(i)), '%Y%m%d') for i in
                                           Environment.one_min_data["open"].ix[self.benchmark].index
                                           if i >= data_transfer.date_str_to_int(self.start)]

        # print(self.benchmark, self.start, self.end, self.period, self.rights_adjustment, self.run_mode)
        self.bar_index = 0
        while True:
            try:
                self.timetag = Environment.benchmark_index[self.bar_index]
            except IndexError:
                if self.run_mode == RunMode.BACKTESTING.value:
                    if save_trade_record:
                        run_backtesting_analysis_engine(self)

                    break
                elif self.run_mode == RunMode.TRADE.value:
                    '''读取最新tick, 更新最新的分钟或者日线
                    if 读取最新tick, 更新最新的分钟或者日线 == done:
                        daily_data.append(new_day_data)
                        self.bar_index += 1
                        benchmark_index.append(new_day_timetag)
                    '''
                    pass

            else:

                date = int(data_transfer.millisecond_to_date(millisecond=self.timetag, format="%Y%m%d"))
                run_bar_engine(self)

        @abstractmethod
        def initialize(self):
            pass

        @abstractmethod
        def handle_bar(self, event):
            pass
