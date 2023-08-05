
-----------------

# feature_stuff: a python machine learning library for advanced feature extraction, processing and interpretation.

<table>
<tr>
  <td>Latest Release</td>
  <td>
    <a href="https://pypi.org/project/feature-stuff/"> see on pypi.org</a>
  </td>
</tr>
<tr>
  <td>Package Status</td>
  <td>
		<a href="https://pypi.org/project/feature-stuff/">see on pypi.org</a>
    </td>
</tr>
<tr>
  <td>License</td>
  <td>
    <a href="https://github.com/hiflyin/Feature-Stuff/blob/master/LICENSE">  see on github</a>
</td>
</tr>
<tr>
  <td>Build Status</td>
  <td>
    <a href="https://travis-ci.org/hiflyin/Feature-Stuff/"> see on travis
    </a>
  </td>
</tr>
</table>



## What is it

**feature_stuff** is a Python package providing fast and flexible algorithms and functions
for extracting, processing and interpreting features. It includes functions like feature interaction extraction
from from boosted decision tree based models, generic target encoding and memory efficient enrichment of features
dataframe with group values.


## How to get it

Binary installers for the latest released version are available at the [Python
package index](https://pypi.org/project/feature-stuff) .

```sh
# or PyPI
pip install feature_stuff
```

The source code is currently hosted on GitHub at:
https://github.com/hiflyin/Feature-Stuff


## Installation from sources

In the `Feature-Stuff` directory (same one where you found this file after
cloning the git repo), execute:

```sh
python setup.py install
```

or for installing in [development mode](https://pip.pypa.io/en/latest/reference/pip_install.html#editable-installs):

```sh
python setup.py develop
```

Alternatively, you can use `pip` if you want all the dependencies pulled
in automatically (the `-e` option is for installing it in [development
mode](https://pip.pypa.io/en/latest/reference/pip_install.html#editable-installs)):

```sh
pip install -e .
```

## How to use it

Example on extracting interactions form tree based models and adding
them as new features to your dataset.

```python
import feature_stuff as fs
import pandas as pd
import xgboost as xgb

data = pd.DataFrame({"x0":[0,1,0,1], "x1":range(4), "x2":[1,0,1,0]})
print data
   x0  x1  x2
0   0   0   1
1   1   1   0
2   0   2   1
3   1   3   0

target = data.x0 * data.x1 + data.x2*data.x1
print target.tolist()
[0, 1, 2, 3]

model = xgb.train({'max_depth': 4, "seed": 123}, xgb.DMatrix(data, label=target), num_boost_round=2)
fs.addInteractions(data, model)

# at least one of the interactions in target must have been discovered by xgboost
print data
   x0  x1  x2  inter_0
0   0   0   1        0
1   1   1   0        1
2   0   2   1        0
3   1   3   0        3

# if we want to inspect the interactions extracted
from feature_stuff import model_features_insights_extractions as insights
print insights.get_xgboost_interactions(model)
[['x0', 'x1']]
```

## Contributing to feature-stuff

All contributions, bug reports, bug fixes, documentation improvements, enhancements and ideas are welcome.

