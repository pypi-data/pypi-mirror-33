import argparse

from .fizzbuzz import fizzbuzz


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--number', type=int, default=100,
                        help='number for fizzbuzz to count to')
    args = parser.parse_args()
    fizzbuzz(args.number)


if __name__ == "__main__":
    main()
