Code associated with the paper: 
Bajgar, O., Kadlec, R., and Kleindienst, J. *A Boo(n) for Evaluating Architecture Performance*. ICML 2018.

## Use Boo<sub>n</sub> !
You can find a Python implementation of the empirical estimator of Boo<sub>n</sub> in `boon/boon.py`. You can also install
it using

```bash
pip install git+https://gitlab.com/obajgar/boon.git
```

Then, having your validation results in the `valid` array and the corresponding test results in the `test` array, you can calculate e.g. Boo<sub>5</sub> using
```python
from boon import boo
boo5 = boo(valid, test, n=5, best='max')
```
The `best='max'` (default) indicates that you are using a metric where higher is better (e.g. accuracy). For metrics such as the error rate, set `best='min'`.


## Work in progress
We are still tidying up some of the code for release. However, we are gradually making it available.

## Data analysis
The notebook `notebooks/PerformanceDistributions.ipynb` captures the analysis performed for Section 4.

## Data
Data used to produce the results can be found in `notebooks/results`.


## License
© Copyright IBM Corporation. 2018.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
