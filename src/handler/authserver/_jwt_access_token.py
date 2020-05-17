import jwt


def read_yggt(access_token_string):
    if len(access_token_string) == 32:
        return access_token_string
    elif len(access_token_string) == 36:
        return access_token_string.replace("-", "")
    else:
        return jwt.decode(access_token_string, verify=False)["yggt"]
