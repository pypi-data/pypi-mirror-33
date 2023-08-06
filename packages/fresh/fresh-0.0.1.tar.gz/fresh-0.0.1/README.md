## Automate the automated...

**Please note: This is not ready, not even for alpha use**

Create a competent model, without ML experience or fuss.
   
Any dataset with a target to predict; continuous, categorical, with features of text, 
numbers, dates.. doesn't matter; `Fresh` will figure it out. 

Build Status:
- OSX & Linux: [![Build Status](https://travis-ci.org/milesgranger/fresh.svg?branch=master)](https://travis-ci.org/milesgranger/fresh)
- Windows: [![Build status](https://ci.appveyor.com/api/projects/status/aebw7ur7mcnadh8o/branch/master?svg=true)](https://ci.appveyor.com/project/milesgranger/fresh/branch/master)

```python
import pandas as pd
from fresh import Model

df = pd.read_csv('mydata.csv')
target = df['my-target']
del df['my-target']

model = Model()
model.fit(df, target)

X = pd.read_csv('new_data_without_answers.csv')
predictions = model.predict(X)
```


---

#### Required Infrastructure: (_not implemented yet_)  

_Will attempt to use these avenues in order listed_

- Run with workers on a Redis job Queue...
    - Set `FRESH_REDIS=<redis uri>`
    - Workers should have `fresh` installed, started with `fresh watch <redis uri>`
    
- Run with Spark...
    - Set `FRESH_SPARK_MASTER=<spark master uri>`
    
- Run locally using multiprocessing lib.
    - Defaults to this if neither of the other two environment variables are found.


