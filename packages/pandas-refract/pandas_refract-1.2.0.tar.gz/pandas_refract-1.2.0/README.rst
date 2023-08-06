
======================================
``pandas-refract``: Convenient partitioning by Truthy/Falsey array
======================================

**pandas-refract** is an MIT licensed Python package with a simple function that allows users to divide their 
dataframes by the 'Truthy' and 'Falseyness' of a provided array.
 
Eventually, the goal of this package is an additional feature to the Pandas library that allows users to .pop rows 
from a dataframe where a condition is met. As far as I can tell this is not possible like the below example.

Ideal case would be::

    target_df = df.pop(df['target_column'] == 'target_value')
    non_target_df = df
    
What is required now is::

    target_df = df[df['target_column'] == 'target_value'] 
    non_target_df = df[df['target_column'] != 'targe_value']
    
    
Obviously, this package is not providing anything not currently possible in the current Pandas library. It does,
however, add a layer of convenience for more complex slicing where you need to separate, not remove, rows by conditions.


Examples
========

Simplest example of current Pandas requires::
 
    df1 = df[df.column.notnull()].reset_index(drop=True)
    df2 = df[df.column.isnull()].reset_index(drop=True)
    
or::

    df1 = df[df.column == 'test_string'].reset_index(drop=True)
    df2 = df[df.column != 'test_string'].reset_index(drop=True)
 
 
With pandas-refract this becomes::
    
    df1, df2 = refract(df, df.column.notnull(), True]
    
and::

    df1, df2 = refract(df, df.column == test_string', True]   
    
    
But you don't have to pass it explicit boolean arrays::
    
    data = {'a': ['', 'truthy', '', 'truthy'],
            'b': [0, 1, 2, 3]
            }
    
    df = pd.DataFrame(data)
    
    truthy_df, falsey_df = refract(df, df.a)
    
    
More complex examples:
*(where 'a' is Falsey and 'b' is an odd number)*
::
      
    df1, df2 = refract(df, ((~df.a) & (df.b % 2 == 1)))
         
