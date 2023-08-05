import argparse
import logging
import sys

from multicrypto.address import validate_address, validate_wif_private_key
from multicrypto.coins import coins, validate_coin_symbol
from multicrypto.network import send

logger = logging.getLogger(__name__)


def get_args():
    parser = argparse.ArgumentParser(
        description='Send cryptocurrency to specified address. Supported coins are: {}'.format(
            ','.join(coin['name'].title() for coin in coins.values() if coin.get('api'))))
    parser.add_argument('-p', '--wif_private_keys', type=str, required=True,
                        help='Comma separated private keys in WIF format which funds will be used'
                             ' to send funds')
    parser.add_argument('-a', '--address', type=str, required=True,
                        help='Address to which we want to send')
    parser.add_argument('-c', '--coin_symbol', type=str, required=True, help='Symbol of the coin \
                        for which we want to make money transfer')
    parser.add_argument('-s', '--satoshis', type=int, required=True,
                        help='How many satoshis you want to send')
    parser.add_argument('-f', '--fee', type=str, required=False, default='1000',
                        help='Transaction fee')
    parser.add_argument('-n', '--minimum_input_threshold', type=int, required=False, default=None,
                        help='Use only inputs containing satoshis equal or above the specified '
                             'threshold')
    parser.add_argument('-x', '--maximum_input_threshold', type=int, required=False, default=None,
                        help='Use only inputs containing satoshis below or equal to the specified '
                             'threshold')

    return parser.parse_args()


def send_crypto(args):
    logging.basicConfig(level=logging.INFO, format='%(message)s', stream=sys.stdout)
    coin_symbol = args.coin_symbol.upper()
    address = args.address
    wif_private_keys = args.wif_private_keys.split(',')
    satoshis = args.satoshis
    fee = int(args.fee)
    minimum_input_threshold = args.minimum_input_threshold
    maximum_input_threshold = args.maximum_input_threshold
    if minimum_input_threshold is not None and minimum_input_threshold <= 0:
        logger.error('Minimum input threshold must be positive')
        return
    if maximum_input_threshold is not None and maximum_input_threshold <= 0:
        logger.error('Maximum input threshold must be positive')
        return
    if minimum_input_threshold and maximum_input_threshold and \
            minimum_input_threshold > maximum_input_threshold:
        logger.error('Minimum input threshold cannot be bigger than maximum input value!')
        return
    try:
        validate_coin_symbol(coin_symbol)
        validate_address(address, coin_symbol, is_script=False)
        for wif_private_key in wif_private_keys:
            validate_wif_private_key(wif_private_key, coin_symbol)
    except Exception as e:
        logger.error(e)
        return
    if not coins[coin_symbol].get('api'):
        logger.error('No api has been defined for coin {}'.format(coin_symbol))

    try:
        result = send(coins[coin_symbol], wif_private_keys, address, satoshis, fee,
                      minimum_input_threshold, maximum_input_threshold)
    except Exception as e:
        logger.error(e)
        return

    return result


def main():
    args = get_args()
    result = send_crypto(args)
    print(result)


if __name__ == '__main__':
    main()
