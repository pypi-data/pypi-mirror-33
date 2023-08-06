from dataclasses import dataclass


@dataclass
class TrustedSource:
    name: str
    url: str


tencent = TrustedSource('Tencent',
                        'https://mirrors.cloud.tencent.com/pypi/simple')

douban = TrustedSource('Douban', 'https://pypi.doubanio.com/simple')

pypi = TrustedSource('Pypi', ' https://pypi.org/simple')

aliyun = TrustedSource('Aliyun', ' https://mirrors.aliyun.com/pypi/simple/')

sources = {}

sources['Tencent'] = tencent
sources['Douban'] = douban
sources['Pypi'] = pypi
sources['Aliyun'] = aliyun


def __dir__():
    return ['sources']
