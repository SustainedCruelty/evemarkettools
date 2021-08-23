# evemarkettools

evemarkettools is a simple python library for pulling price data from the EVE ESI.
It also contains functions to convert type_ids, system_ids, region_ids etc. into their respective names and vice versa.

## Installation

Use the package manager [pip](https://pypi.org/project/evemarkettools/) to install evemarkettools.

```bash
pip install evemarkettools
```

## Usage

```python
import evemarkettools as emt

emt.typeNameToID('Sabre') # returns 22456
emt.regionNameToID('The Forge') # returns 10000002
emt.item_price(22456, region_id=10000002, order_type='sell') # returns 63560000
emt.item_quantity_price(22456, quantity=100, region_id=10000002) # returns 6531720000

```
Check out this [colab-notebook](https://colab.research.google.com/drive/1XipQmxwsY9LW6sSaxfjr5VNgzWtifIA2?usp=sharing) to see what other function the library provides

## License
[MIT](https://choosealicense.com/licenses/mit/)
