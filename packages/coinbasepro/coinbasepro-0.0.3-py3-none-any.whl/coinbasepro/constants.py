from enum import Enum


class CurrencyPairs(Enum):
    BTCUSD = 1


if __name__ == '__main__':
    x = CurrencyPairs.BTCUSD
    print(x)
