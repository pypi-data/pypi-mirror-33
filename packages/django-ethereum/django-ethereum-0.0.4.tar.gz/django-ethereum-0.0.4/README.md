# Django Ethereum Utilities

A collection of helpers to make it easier to work with Ethereum from your Django app.

Currently this only consists of a custom model field which stores Ethereum addresses
in the checksummed format.

## Install

`pip install django-ethereum`


## Fields

### `EthereumAddressField`


A `CharField` which automatically converts an Ethereum address into its checksummed
representation.

```python
    from django_ethereum.fields import EthereumAddressField

    class MyModel(models.Model):
        address = EthereumAddressField()

    my_model = MyModel(address="0x627306090abab3a6e1400e9345bc60c78a8bef57")
    my_model.save()
    print(my_model.address)
    "0x627306090abaB3A6e1400e9345bC60c78a8BEf57"  # Note capitalisation
```

If the address is invalid a ``ValidationError`` will be raised.

Note that the address is stored in the checksummed format. If you want to compare against
a non-checksummed address you will need to perform a case-insensitive match (or preferably convert
the address to a checksummed address before comparing):

```python
    MyModel.objects.filter(address__iexact=non_checksummed_address)
    # Or
    MyModel.objects.filter(address__iexact=Web3.toChecksumAddress(non_checksummed_address))
```