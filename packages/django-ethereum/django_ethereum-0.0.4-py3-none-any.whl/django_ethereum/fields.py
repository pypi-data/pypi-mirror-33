from django.db import (
    models,
)
from django.utils.translation import (
    gettext_lazy as _,
)
from django_ethereum.validators import (
    EthereumAddressValidator,
)
from web3 import Web3


class EthereumAddressField(models.CharField):
    description = _("Ethereum address with automatic checksum")

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 42
        super().__init__(*args, **kwargs)
        self.validators.append(EthereumAddressValidator())

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs

    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)
        # Only validate if value is not empty, in case field is used with `null=True`
        if value:
            value = Web3.toChecksumAddress(value)
            setattr(model_instance, self.attname, value)
        return value
