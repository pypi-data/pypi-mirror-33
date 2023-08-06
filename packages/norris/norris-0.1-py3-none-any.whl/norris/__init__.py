from requests import get
from pandas import DataFrame

def get_random_joke():
    random_joke = get("http://api.icndb.com/jokes/random?escape=javascript")
    return random_joke.json()['value']['joke']

def get_numbered_joke(n):
    assert type(n) == int, 'n is not type int'

    n = str(n)

    numbered_joke = get("http://api.icndb.com/jokes/" + n + "?escape=javascript")

    if numbered_joke.json()['type'] == 'success':
        return numbered_joke.json()['value']['joke']

    else:
        return 'That joke number is unavailable.'

def get_multiple_randos(n):
    assert type(n) == int, 'n is not type int'

    n = str(n)

    multiple_randos = get("http://api.icndb.com/jokes/random/" + n + "?escape=javascript")

    return DataFrame(multiple_randos.json()['value'])[['id', 'joke']]
