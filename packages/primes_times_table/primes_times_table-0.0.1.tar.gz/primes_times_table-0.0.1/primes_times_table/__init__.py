"""
This program prints out a multiplication table of the first 10 primes.
- first row and column should have ten primes
"""
import sys
import math


def is_prime(num):
    divisor = 2
    while divisor <= num ** 0.5:
        if num % divisor == 0:
            return False
        divisor += 1
    return True


def genprimes(count):
    """
    naive prime solver using is_prime checks

    https://en.wikipedia.org/wiki/Prime_number_theorem

    Note: this is an approximation that assumes primes occur evenly
    O(n) * O(n * (n ^0.5)) ->> O(n^2.5)

    TODO: refactor with a prime number sieve
    """
    primes = [None] * count
    num = 2
    n = 0
    while n < count:  # assuming O(n), todo: use PNT for more detailed approx.
        while not is_prime(num):  # O(n*(n^0.5))
            num += 1
        primes[n] = num
        num += 1
        n += 1
    return primes


def print_row(iterable, first_item, max_value):
    spacing = int(math.log(max_value, 10) + 2)  # base 10 number length + 1 space
    num_format = '{:-{}}'
    if not first_item:
        prefix = ' ' * spacing
    else:
        prefix = num_format.format(first_item, spacing)

    print(prefix + ''.join(num_format.format(v, spacing) for v in iterable))


def primes_times_table(n):
    """
    O(n^2 / log(n)) [naive primes generation] + O(n^2)[print rows * cols]
    O(n) space complexity
    """
    primes = genprimes(n)
    max_value = primes[-1] ** 2

    print_row(primes, None, max_value)
    for row in primes:
        print_row((row * col for col in primes), row, max_value)


def main_wrapper(argv):
    if len(argv) > 1:
        n = int(argv[1])
    else:
        n = 10
    print('Multiplication table for first [%i] primes:' % n)
    primes_times_table(n)


def main():
    main_wrapper(sys.argv)


if __name__ == '__main__':
    main()
