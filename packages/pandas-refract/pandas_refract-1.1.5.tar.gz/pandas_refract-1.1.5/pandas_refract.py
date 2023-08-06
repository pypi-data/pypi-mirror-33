import numpy as np


__title__ = "pandas-refract"
__version__ = "1.1.5"
__author__ = "Nicholas Lawrence"
__license__ = "MIT"
__copyright__ = "Copyright 2018-2019 Nicholas Lawrence"


def refract(df, conditional, reset_index=True):
    """

    Return pair of Dataframes split against Truthy and Falseyness of provided array. Option to reset index in place.

    / >>> data = {'temperature': ['high', 'low', 'low', 'high'],
                  'overcast': [True, False, True, False]
                  }

    / >>> df = pandas.DataFrame(data)

    / >>> hot_df, cold_df = refract(df, df.temperature == 'high')

    / >>> overcast_df, not_overcast_df = refract(df, df.overcast, reset_index=True)

    / >>> print(overcast_df.iloc[0], not_overcast_df.iloc[0])

    """
    _conditional = np.asarray(conditional, bool)

    if reset_index:
        return df[_conditional].reset_index(drop=True),\
               df[~_conditional].reset_index(drop=True)

    return df[_conditional], df[~_conditional]
