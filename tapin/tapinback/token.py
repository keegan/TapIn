import secrets

def gen_token():
    return secrets.token_bytes(672)
