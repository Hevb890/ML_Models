# -*- coding: utf-8 -*-
"""House_Price_Predictor.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Ow3yaCWTvkmQQEDlPl0uVqLlUgi6Mxrd
"""

import pandas as pd

fed_files = ["https://raw.githubusercontent.com/dataquestio/project-walkthroughs/master/house_prices/CPIAUCSL.csv","https://raw.githubusercontent.com/dataquestio/project-walkthroughs/master/house_prices/MORTGAGE30US.csv","https://raw.githubusercontent.com/dataquestio/project-walkthroughs/master/house_prices/RRVRUSQ156N.csv"]
dfs = [pd.read_csv(f, parse_dates=True, index_col=0) for f in fed_files]

dfs[0]

fed_data = pd.concat(dfs, axis=1)

fed_data = fed_data.ffill() # Forward fill function

fed_data.tail(30)

zillow_files = ["https://raw.githubusercontent.com/dataquestio/project-walkthroughs/master/house_prices/Metro_median_sale_price_uc_sfrcondo_week.csv","https://raw.githubusercontent.com/dataquestio/project-walkthroughs/master/house_prices/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_month.csv"]

zillow_dfs = [pd.read_csv(f) for f in zillow_files]

zillow_dfs[0]

zillow_dfs = [pd.DataFrame(df.iloc[0,5:]) for df in zillow_dfs]

zillow_dfs[0]

for df in zillow_dfs:
  df.index = pd.to_datetime(df.index)
  df['month'] = df.index.to_period('M')

zillow_dfs[0]

price_data = zillow_dfs[0].merge(zillow_dfs[1], on="month")

price_data.index = zillow_dfs[0].index

price_data

del price_data['month']
price_data.columns = ["price", "value"]

price_data

fed_data = fed_data.dropna()

fed_data.tail(20)

from datetime import timedelta
#shift fed data index by two days
fed_data.index = fed_data.index + timedelta(days=2)

fed_data.tail(20)

# Merging 2 data frames
price_data = fed_data.merge(price_data, left_index=True, right_index=True)

price_data

price_data.columns = ["cpi","interest","vacancy","price","value"]

price_data

price_data.plot.line(y="price", use_index=True)

price_data["adjusted_price"] = price_data["price"] / price_data["cpi"] * 100

price_data["adjusted_value"] = price_data["value"] / price_data["cpi"] *100

price_data.plot.line(y="adjusted_price", use_index=True)

price_data["next_quarter"] = price_data["adjusted_price"].shift(-13)

price_data

price_data.dropna(inplace=True)

price_data

# Target Variable
price_data["change"] = (price_data["next_quarter"] > price_data["adjusted_price"]).astype(int)

price_data["change"].value_counts()

predictors = ["interest","vacancy","adjusted_price","adjusted_value"]
target = ["change"]

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import numpy as np

START = 260
STEP = 52 # 52 WEEKS PER QUARTER

def predict(train, test, predictors, target):
  model = RandomForestClassifier(min_samples_split=10, random_state=1)
  model.fit(train[predictors], train[target])
  preds = model.predict(test[predictors])
  return preds

def backtest(data, predictors, target):
  all_preds = []
  for i in range(START, data.shape[0], STEP):
    train = price_data.iloc[:i]
    test = price_data.iloc[i:(i+STEP)]
    all_preds.append(predict(train, test, predictors, target))

  preds = np.concatenate(all_preds)
  return preds, accuracy_score(data.iloc[START:][target],preds)

preds, accuracy = backtest(price_data, predictors, target)

accuracy

"""Improving Accuracy"""

yearly = price_data.rolling(52, min_periods=1).mean()

yearly

yearly_ratio = [p + "_year" for p in predictors]
price_data[yearly_ratio] = price_data[predictors] / yearly[predictors]

preds, accuracy = backtest(price_data, predictors + yearly_ratio, target)

accuracy

pred_match = (preds == price_data[target].iloc[START:])

pred_match[pred_match == True] = "green"
pred_match[pred_match == False] = "red"

import matplotlib.pyplot as plt

plot_data = price_data.iloc[START:].copy()

plot_data.reset_index().plot.scatter(x="index", y="adjusted_price", color=pred_match)

from sklearn.inspection import permutation_importance

model = RandomForestClassifier(min_samples_split=10, random_state=1)
model.fit(price_data[predictors], price_data[target])

result = permutation_importance(model, price_data[predictors], price_data[target], n_repeats=10, random_state=1)

result["importances_mean"]

predictors

