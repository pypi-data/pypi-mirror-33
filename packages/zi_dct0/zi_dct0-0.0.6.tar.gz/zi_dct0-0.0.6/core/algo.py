import logging
from enum import Enum


class DCEventType(Enum):
    UPTURN = 1
    DOWNTURN = 2
    OVERSHOOT = 3


class TradeStrategy(Enum):
    TF = 1
    CT = 2


class Config:
    def __init__(self, strategy, delta_p, initial_mode=None, initial_p_ext=None):
        self.strategy = strategy
        self.delta_p = delta_p
        if initial_mode is None and initial_p_ext is None:
            if strategy == TradeStrategy.TF:
                self.initial_mode = DCEventType.UPTURN
                self.initial_p_ext = 0.0
            else:
                self.initial_mode = DCEventType.DOWNTURN
                self.initial_p_ext = 1000000000.0
        else:
            self.initial_mode = initial_mode
            self.initial_p_ext = initial_p_ext


class ZI_DCT0:
    def __init__(self, logger, config: Config):
        self.logger = logger
        self.config = config
        self.mode = config.initial_mode
        self.current_event = DCEventType.OVERSHOOT
        self.p_ext = config.initial_p_ext
        pass

    def observe(self, p_t):
        if self.config is None:
            self.logger.error('No configuration')
            return
        self.logger.debug('p_ext={} p_t={}'.format(self.p_ext, p_t))
        if self.mode == DCEventType.UPTURN:
            if p_t <= self.p_ext * (1.0 - self.config.delta_p):
                self.mode = DCEventType.DOWNTURN
                self.current_event = DCEventType.DOWNTURN
                self.p_ext = p_t
            else:
                self.p_ext = max([self.p_ext, p_t])
                self.current_event = DCEventType.OVERSHOOT

        else:  # initial_mode is DOWNTURN
            if p_t >= self.p_ext * (1.0 + self.config.delta_p):
                self.mode = DCEventType.UPTURN
                self.current_event = DCEventType.UPTURN
                self.p_ext = p_t
            else:
                self.p_ext = min([self.p_ext, p_t])
                self.current_event = DCEventType.OVERSHOOT

        return self.current_event

    def is_buy_signaled(self):
        buy_signaled = (TradeStrategy.TF == self.config.strategy and DCEventType.UPTURN == self.current_event) or (
            TradeStrategy.CT == self.config.strategy and DCEventType.DOWNTURN == self.current_event)
        return buy_signaled

    def is_sell_signaled(self):
        sell_signaled = (TradeStrategy.TF == self.config.strategy and DCEventType.DOWNTURN == self.current_event) or (
                TradeStrategy.CT == self.config.strategy and DCEventType.UPTURN == self.current_event)
        return sell_signaled
