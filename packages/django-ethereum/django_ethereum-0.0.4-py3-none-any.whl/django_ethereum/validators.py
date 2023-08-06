from django.core.exceptions import (
    ValidationError,
)
from django.utils.translation import (
    gettext_lazy as _,
)
from web3 import Web3


class EthereumAddressValidator:
    message = _("Ensure this value is a valid Ethereum address")

    def __call__(self, value):
        try:
            Web3.toChecksumAddress(value)
        except ValueError as e:
            raise ValidationError(e)
