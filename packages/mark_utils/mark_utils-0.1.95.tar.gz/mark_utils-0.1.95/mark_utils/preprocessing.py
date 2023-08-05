
class Standardize():
    @staticmethod
    def torch(x):
        import torch
        import numpy as np
        """
            Preprocessing the x data with zero meand and unitary variance
            Arguments:
                        x -- numpy ndarray
            Returns:
                        standardized -- data standardize (torch Tensor)
        """

        # Convert to Tensor
        if isinstance(x, np.ndarray):
            x = torch.from_numpy(x)

        standardized = (torch.div(x - torch.mean(x, 0), torch.std(x, 0)))
        return standardized

    @staticmethod
    def numpy(x, bessel_correction=True):
        import numpy as np
        """
            Preprocessing the x data with zero meand and unitary variance
            Arguments:
                        x -- numpy ndarray
            Returns:
                        standardized -- data standardize (numpy ndarray)
        """
        if bessel_correction:
            standardized = (x - np.mean(x, 0)) / np.std(x, 0, ddof=1)
        else:
            standardized = (x - np.mean(x, 0)) / np.std(x, 0)

        return standardized


class Normalize():
    def torch(x):
        import torch
        import numpy as np
        """
                Preprocessing the x data with zero meand and unitary variance
                Arguments:
                            x -- numpy ndarray
                Returns:
                            standardize -- data standardize (torch Tensor)
            """
        # Convert to Tensor
        if isinstance(x, np.ndarray):
            x = torch.from_numpy(x)

        max_ = torch.max(x, 0)[0]
        normilized = torch.div(x, max_)

        return normilized

    @staticmethod
    def numpy(x):
        import numpy as np
        """
                Preprocessing the x data with zero meand and unitary variance
                Arguments:
                            x -- numpy ndarray
                Returns:
                            standardize -- data standardize (numpy ndarray)
            """

        normilized = x / x.max(axis=0)

        return normilized


# def savitzky_golay(y, window_size, order, deriv=0, rate=1):
#
#     import numpy as np
#     from math import factorial
#
#     try:
#         window_size = np.abs(np.int(window_size))
#         order = np.abs(np.int(order))
#     except ValueError, msg:
#         raise ValueError("window_size and order have to be of type int")
#     if window_size % 2 != 1 or window_size < 1:
#         raise TypeError("window_size size must be a positive odd number")
#     if window_size < order + 2:
#         raise TypeError("window_size is too small for the polynomials order")
#     order_range = range(order + 1)
#     half_window = (window_size - 1) // 2
#     # precompute coefficients
#     b = np.mat([[k**i for i in order_range]
#                 for k in range(-half_window, half_window + 1)])
#     m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
#     # pad the signal at the extremes with
#     # values taken from the signal itself
#     firstvals = y[0] - np.abs(y[1:half_window + 1][::-1] - y[0])
#     lastvals = y[-1] + np.abs(y[-half_window - 1:-1][::-1] - y[-1])
#     y = np.concatenate((firstvals, y, lastvals))
#     return np.convolve(m[::-1], y, mode='valid')
