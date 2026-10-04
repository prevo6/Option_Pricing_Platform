import numpy as np
from datetime import datetime, timedelta, time

class BinomialTree:
  
    def __init__(self, S0: float, K: float, T: float, r: float, sigma: float, N: int):
        """
        Initializes the key inputs used for the discrete calculation of the binomial tree
        
        :param self: Description
        :param S0: Current stock price
        :param K: Strike price
        :param T: Time to maturity in years
        :param r: risk free interest rate
        :param sigma: volatility of the underlying
        :param N: Height of the binomial tree
        """

        self.S0 = float(S0)
        self.K = float(K)
        self.T = self.__tenor(T)
        self.r = r
        self.sigma = sigma
        self.N = N


    def __tenor(self, T: datetime) -> float:
       
        contract_end_formatted = datetime.combine(T, time(16, 0, 0))
        expiry = (contract_end_formatted - datetime.now()) / timedelta(days=365)
        return float(expiry)
    

    def calculate_call(self) -> float:
        """Calculates price for put option according to the Binomial formula."""  

        dT = self.T / self.N
        u = np.exp(self.sigma * np.sqrt(dT))                 
        d = 1.0 / u   

        # Price vector initialization
        V = np.zeros(self.N + 1)                       

        # Underlying asset prices at different time points
        S_T = np.array( [(self.S0 * u**j * d**(self.N- j)) for j in range(self.N + 1)])

        a = np.exp(self.r * dT)      # risk free compounded return
        p = (a - d) / (u - d)        # risk neutral up probability
        q = 1.0 - p                  # risk neutral down probability   

        V[:] = np.maximum(S_T - self.K, 0.0)
    
        # Overriding option price 
        for _ in range(self.N - 1, -1, -1):
            V[:-1] = np.exp(-self.r * dT) * (p * V[1:] + q * V[:-1]) 

        return V[0] 

    def calculate_put(self) -> float:

        """Calculates price for put option according to the Binomial formula."""  
        # Delta t, up and down factors
        dT = self.T / self.N                            
        u = np.exp(self.sigma * np.sqrt(dT))                 
        d = 1.0 / u                                    

        # Price vector initialization
        V = np.zeros(self.N+ 1)                       

        # Underlying asset prices at different time points
        S_T = np.array( [(self.S0 * u**j * d**(self.N - j)) for j in range(self.N + 1)])

        a = np.exp(self.r * dT)      # risk free compounded return
        p = (a - d) / (u - d)        # risk neutral up probability
        q = 1.0 - p                  # risk neutral down probability   

        V[:] = np.maximum(self.K - S_T, 0.0)
    
        # Overriding option price 
        for i in range(self.N - 1, -1, -1):
            V[:-1] = np.exp(-self.r * dT) * (p * V[1:] + q * V[:-1]) 

        return V[0]


class BinomialTreeVisual:

    def __init__(self, tree: BinomialTree):
        """
        Class to create visual representation of the tree with performace draw downs
        
        :param tree: Binomial Tree to display
        :type tree: BinomialTree
        """
        self.S0 = tree.S0
        self.K = tree.K
        self.T = tree.T  
        self.r = tree.r
        self.sigma = tree.sigma
        self.N = 5

        self.stock_tree = None
        self.value_tree = None

    def build_tree(self):
        N = self.N
        dT = self.T / N
        u = np.exp(self.sigma * np.sqrt(dT))
        d = 1.0 / u
        a = np.exp(self.r * dT)
        p = (a - d) / (u - d)
        q = 1.0 - p

        # stock_tree[i][j] = stock price at time step i, having gone up j times
        stock_tree = np.zeros((N + 1, N + 1))
        value_tree = np.zeros((N + 1, N + 1))

        for i in range(N + 1):
            for j in range(i + 1):
                stock_tree[i, j] = self.S0 * (u ** j) * (d ** (i - j))

        # terminal payoffs at the last column (i = N)
        for j in range(N + 1):
  
            value_tree[N, j] = max(stock_tree[N, j] - self.K, 0.0)
            

        # backward induction, filling in every earlier layer instead of discarding it
        for i in range(N - 1, -1, -1):
            for j in range(i + 1):
                value_tree[i, j] = np.exp(-self.r * dT) * (
                    p * value_tree[i + 1, j + 1] + q * value_tree[i + 1, j]
                )

        self.stock_tree = stock_tree
        self.value_tree = value_tree
        return value_tree[0, 0]

if __name__ == "__main__":

    BPM = BinomialTree(100.0, 100.0, 1.0, .05, .20, 100)
    print("Call Option Value with 100 Steps:", BPM.calculate_call())

    BPM = BinomialTree(100.0, 100.0, 1.0, .05, .20, 500)
    print("Call Option Value with 500 Steps: ", BPM.calculate_call())

    BPM = BinomialTree(100.0, 100.0, 1.0, .05, .20, 10000)
    print("Call Option Value with 10000 Steps: ", BPM.calculate_call())

    BPM = BinomialTree(100.0, 100.0, 1.0, .05, .20, 100)
    print("Put Option Value with 100 Steps:", BPM.calculate_put())

    BPM = BinomialTree(100.0, 100.0, 1.0, .05, .20, 500)
    print("Put Option Value with 500 Steps: ", BPM.calculate_put())

    BPM = BinomialTree(100.0, 100.0, 1.0, .05, .20, 10000)
    print("Put Option Value with 10000 Steps: ", BPM.calculate_put())