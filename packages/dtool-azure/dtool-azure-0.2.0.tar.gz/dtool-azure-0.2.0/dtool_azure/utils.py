"""Dtool Azure helper functions."""

from dtoolcore.utils import get_config_value


def get_azure_account_key(account_name, config_path):
    """Return the Azure account key associated with the account name."""

    account_key = get_config_value(
        "DTOOL_AZURE_ACCOUNT_KEY_" + account_name,
        config_path=config_path
    )
    return account_key
