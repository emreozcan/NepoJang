from db import Account
from password import password_compare


def account_or_none(username, password):
    accounts = list(Account.select(lambda a: a.username == username))
    if len(accounts) != 1 or not password_compare(password, accounts[0].password):
        return None
    return accounts[0]
