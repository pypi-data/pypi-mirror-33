# Veriteos Python Library

Official Python client library for Veriteos API.

## Documentation

See the [https://docs.veriteos.com/?python](Python API docs).

## Installation

Install the `veriteos` Python package using `pip`:

```
$ pip install --upgrade veriteos
```

### Requirements

- Python 3.5+

## Usage

```python
import veriteos

# Instantiate client
client = veriteos.Client(
    api_key='VERITEOS_API_KEY',
    transaction_family='TRANSACTION_FAMILY',
    transaction_family_version='1.0'
)

# Submit a transaction
client.submit(
    address='my instance',
    transactions=['hello veriteos']
)

# Read state from address
client.read_address(address='my instance')
```

## Troubleshooting

If you notice any problems, please drop us an email at [support@veriteos.com](mailto:support@veriteos.com).
