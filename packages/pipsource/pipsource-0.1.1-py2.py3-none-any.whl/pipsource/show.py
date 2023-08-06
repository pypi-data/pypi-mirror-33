import toml


def current():
    config = toml.load('Pipfile')
    return f"{config['source'][0]['name']:20}{config['source'][0]['url']}"
