from datetime import datetime, timedelta, time
import math
from scipy.stats import norm

class BlackScholes:

    def __init__(self, S: float, K: float, r: float, T: datetime, sigma: float, isCall: bool = True):
        """  
        :param S: Underlying Price
        :type S: float
        :param K: Strike Price
        :type K: float
        :param r: risk free rate
        :type r: float
        :param T: Time till expiration
        :type T: datetime
        :param sigma: Implied volatility
        :type sigma: float
        :param isCall: Is the option a call or not
        :type isCall: bool
        """
        self.S = float(S)
        self.K = float(K)
        self.r = r
        self.T = self.__tenor(T)
        self.sigma = sigma
        self.isCall = isCall

    def __tenor(self, T: datetime) -> float:
        contract_end_formatted = datetime.combine(T, time(16, 0, 0))
        expiry = (contract_end_formatted - datetime.now()) / timedelta(days=365)
        return float(expiry)
    
    def d1(self) -> float:
        return (math.log(self.S / self.K) + (self.r + math.pow(self.sigma, 2)/ 2) * self.T) / (self.sigma * math.sqrt(self.T))

    def d2(self) -> float:
        return self.d1() - self.sigma * math.sqrt(self.T)

    def call(self) -> float:
        """
        Calculates the call option price 
        :return: The theoretical fair price of a call option given input parameters
        :rtype: float
        """
        return (self.S * norm.cdf(self.d1())) - (self.K * math.pow(math.e, -self.r * self.T) * norm.cdf(self.d2()))

    def put(self) -> float:
        """
        Calculates the put option price 
        :return: The theoretical fair price of a put option given input parameters
        :rtype: float
        """
        return (self.K * math.pow(math.e, -self.r * self.T) * norm.cdf(-self.d2())) - (self.S * norm.cdf(-self.d1()))

    def delta(self) -> float:
        return norm.cdf(self.d1()) if self.isCall else norm.cdf(self.d1()) - 1
    
    def gamma(self) -> float:
        return norm.pdf(self.d1()) / (self.S * self.sigma * math.sqrt(self.T))


    def theta(self) -> float:
        """
        Option price decay per calendar day.
        Assumes a non-dividend-paying underlying.
        """
        decay = -(self.S * self.sigma * norm.pdf(self.d1())) / (2 * math.sqrt(self.T))

        if self.isCall:

            annual = decay - self.r * self.K * math.exp(-self.r * self.T) * norm.cdf(self.d2())

        else:
            annual = decay + self.r * self.K * math.exp(-self.r * self.T) * norm.cdf(-self.d2())

        return annual / 365
        

    def vega(self) -> float:
        """Option price change per 1 percentage-point move in volatility."""

        return self.S * math.sqrt(self.T) * norm.pdf(self.d1()) / 100

    def rho(self) -> float:
        """Option price change per 1 percentage-point move in the risk-free rate."""

        discount = self.K * self.T * math.exp(-self.r * self.T)

        if self.isCall:

            return discount * norm.cdf(self.d2()) / 100
        
        return -discount * norm.cdf(-self.d2()) / 100


if __name__ == "__main__":
    print(BlackScholes(200, 224, .15, datetime(2026, 9, 25), .15, isCall=False).gamma())

