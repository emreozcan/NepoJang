from db import Account
from password import password_compare


def account_or_none(username, password):
    account = Account.get(lambda a: a.username == username)
    if account is None or not password_compare(password, account.password):
        return None
    return account
