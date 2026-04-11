from typing import Union, Optional, Tuple

import numpy as np
from scipy.stats import gaussian_kde
import scipy.integrate as integrate

# --------------------------------
def isin01(x) -> bool:
    return (x >= 0) & (x <= 1)
# --------------------------------
def validate_vec(x) -> None:
    if not isinstance(x, np.ndarray):
        raise TypeError(f"expect numpy vector, but got {type(x)}")
    if len(x.shape) != 1:
        raise TypeError(f"expect numpy vector, but got an array")
    if len(x) < 1:
        raise ValueError("numpy vector is too short")
    if any(np.isnan(x)):
        raise ValueError(f"found {sum(np.isnan(x))} NaN out of {len(x)}")
    if any(np.isinf(x)):
        raise ValueError(f"found {sum(np.isinf(x))} NaN out of {len(x)}")
    return None
# --------------------------------
def validate_normqt(x) -> None:
    if not isinstance(x, tuple):
        raise TypeError(f"expect a 2-tuple of floats but got {type(x)}")
    if len(x) != 2:
        raise TypeError(f"expect a 2-tuple of floats but got {len(x)} elements in the tuple")
    if not isinstance(x[0],float):
        raise TypeError(f"expect 1st element to be float but got {type(x[0])}")
    if not isinstance(x[1],float):
        raise TypeError(f"expect 2nd element to be float but got {type(x[1])}")
    if not isin01(x[0]):
        raise ValueError(f"expect 1st element to be in [0,1] but got {x[0]}")
    if not isin01(x[1]):
        raise ValueError(f"expect 1st element to be in [0,1] but got {x[1]}")
    if x[0] >= x[1]:
        raise ValueError("2nd element should be greater than 1st element")
    return None

# --------------------------------
class HoldenWulfsberg2009:
    """Implementing the FWCP estimator in
    Holden, S. and Wulfsberg, F. (2009). How strong is the macroeconomic case for downward real wage rigidity? Journal of Monetary Economics, 56(4):605–615.

    ## Usage (basic)
    ```python
    import numpy as np
    
    datRef = np.random.laplace(loc = 0.05, scale = 3.2, size = 200)
    datObs = np.random.randn(100) + 0.05
    
    hw09 = HoldenWulfsberg2009(datRef)
    
    Z = hw09.rescale_dat(datObs)[0]
    
    resFreq = hw09.fwcp_freq(datObs)
    resInt  = hw09.fwcp_int(datObs, weighted = False) # integration weighted by |x|
    ```

    ## Usage (consistency check)
    ```python
    # check correlation between freq method FWCP and integration method FWCP
    import tqdm
    res = {
        "freq" : [],
        "int"  : []
    }
    for i in tqdm.tqdm(range(5000)):
        datRef = np.random.laplace(loc = 0.05, scale = 3.2, size = 200)
        datObs = np.random.randn(100) + 0.05
        
        hw09 = HoldenWulfsberg2009(datRef)
        
        Z = hw09.rescale_dat(datObs)[0]
        
        resFreq = hw09.fwcp_freq(datObs)
        resInt  = hw09.fwcp_int(datObs, weighted = False)
    
        res["freq"].append(resFreq)
        res["int"].append(resInt)
    
    plt.scatter(res["freq"],res["int"])
    plt.xlabel("freqency")
    plt.ylabel("integral")
    plt.title(f"corr = {round(np.corrcoef(res["freq"],res["int"])[0,1],3)}")
    ```
    """
    def __init__(
        self,
        refDat : np.ndarray,
        topCut : float = 0.25,
        normQt : Tuple[float,float] = (0.35,0.75)
    ):
        """Initializing the class by constructing notional distribution using a given data sample

        Args:
        - refDat: a vector of reference wage growth observations, in either percentage points (1 for 1% growth) or digital (0.01 for 1% growth).
        - topCut: slicing how much top growth observations to construct the notional distribution.
        - normQt: two quantiles used to normalize the notional distribution; first < second required
        """
        validate_vec(refDat)
        validate_normqt(normQt)
        if not isin01(topCut):
            raise ValueError(f"topCut should be in [0,1] but got {topCut}")

        # caution: actual quantile is 1 - topCut, not topCut
        datTop = refDat[refDat >= np.quantile(refDat, 1 - topCut)]

        # symmetry assumption: mirroring
        datMid = datTop.min()
        G = np.concatenate((datTop, 2 * datMid - datTop), axis = 0)
        self.datNotional = (G - datMid) / (np.quantile(G,normQt[1]) - np.quantile(G,normQt[0]))

        self.topCut = topCut
        self.normQt = normQt
        return None

    def rescale(self, locPar : float, scalePar : float) -> np.ndarray:
        """Re-scaling the normalized G(0,1) notional distribution to G(locPar,scalePar)
        """
        return self.datNotional * scalePar + locPar
        
    def rescale_dat(self, datObs : np.ndarray) -> np.ndarray:
        validate_vec(datObs)
        qtObs  = np.quantile(datObs, self.normQt)
        midObs = np.median(datObs)
        return (self.rescale(midObs, qtObs[1] - qtObs[0]), qtObs, midObs)

    def fwcp_freq(self, datObs : np.ndarray) -> float:
        """Fraction of Wage Cuts Prevented (FWCP) by frequency method
        pActual = #{dw<0}/#obsActual
        pNotion = #{z<0}/#obsNotional
        z = G01 * (qtActual75 - qtActual35) + muActual, muActual is median rather than mean

        fwcp := 1 - pActual / pNotion
        
        returns -Inf if no prevented job cuts found.
        """
        Z = self.rescale_dat(datObs)[0]
        pActual = sum(datObs < 0) / len(datObs)
        pNotion = sum(Z < 0) / len(Z)

        return float(1 - pActual / pNotion) if pNotion != 0 else -np.inf

    def fwcp_int(self, datObs : np.ndarray, weighted : bool = True, bw_method : str = "scott") -> float:
        """Fraction of Wage Cuts Prevented (FWCP) by frequency method
        fwcp (unweighted) = int_{-inf}^{median{datObs}} G(x) - F(x) dx
        fwcp (weighted) = int_{-inf}^{median{datObs}} abs(x) * (G(x) - F(x)) dx

        where G(x) is a fitted density function of the notional distribution transformed from G(0,1),
        and F(x) is a fitted density function of the actual distribution.

        Interpolated kernel density with Scott/Silverman's rule of bandwidth selection.
        """
        Z, qtObs, ub = self.rescale_dat(datObs)

        lb = min(datObs.min(), Z.min())

        kdeActual = gaussian_kde(datObs, bw_method = bw_method)
        kdeNotion = gaussian_kde(Z, bw_method = bw_method)
        
        def integrand(x, weighted : bool = weighted):
            wt = abs(x) if weighted else 1.0
            return wt * (kdeNotion.evaluate(x)[0] - kdeActual.evaluate(x)[0])

        return integrate.quad(integrand, lb, ub)[0]
