import hashlib
import requests

name = "safepass"
API_BASE = 'https://api.pwnedpasswords.com/range/'


def safepass(passwd):
    hashed = hashlib.sha1(passwd).hexdigest().upper()
    page = requests.get(API_BASE + hashed[:5])
    for line in page.text.split('\n'):
        suffix, count = line.split(':')
        count = int(count)
        if hashed.endswith(suffix):
            if count > 0:
                print('NOT SAFE!')
                return False
            break
    print('SAFE')
    return True
