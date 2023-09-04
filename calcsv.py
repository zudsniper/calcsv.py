#!/usr/bin/env python3
# v0.3.2
import argparse
import csv
import json
import threading
import time
from statistics import mean, median, stdev
from colorama import init, Fore, Back, Style
from loguru import logger
from tabulate import tabulate
import sys
from decouple import config

# Initialize colorama
init()


# Define the dynamic data structure
class Transaction:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# Load configurations from .env
CSV_FORMAT = config('FORMAT', default="date,amount,,,description")
CLASSIFIER_FILE = config('CLASSIFIER_FILE', default='static_classes.json')
DEFAULT_CLASSIFIER = config('CLASSIFIER_TYPE', default='normal')

# Load static classes
try:
    with open(CLASSIFIER_FILE, 'r') as f:
        STATIC_CLASSES = json.load(f)
except Exception as e:
    logger.error(f"{Fore.RED}Failed to load {CLASSIFIER_FILE}: {e}{Fore.RESET}")
    sys.exit(1)

# Modify logger to be pretty
logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO", colorize=True)


# classify transactions using the consecutive substrings listed in static_classes.json -- for `normal` classifier
def classify(transaction):
    for class_name, keywords in STATIC_CLASSES.items():
        for keyword in keywords:
            if keyword.lower() in transaction.description.lower():
                return class_name
    return None


# Loading spinner (silly rainbow) to show that the program is still running
def loading_spinner():
    emojis = ["🔴", "🟠", "🟡", "🟢", "🔵", "🟣", "🟤"]
    idx = 0
    while not stop_spinner:
        print(f"\r{emojis[idx % len(emojis)]} Processing...", end="")
        idx += 1
        time.sleep(0.2)


def main():
    parser = argparse.ArgumentParser(description='Parse and classify CSV transactions.')
    parser.add_argument('filepath', type=str, help='Path to the CSV file.')
    parser.add_argument('--format', '-f', type=str, default=CSV_FORMAT, help='CSV format.')
    parser.add_argument('--classifier', '-c', choices=['normal', 'ai', 'hybrid'], default=DEFAULT_CLASSIFIER,
                        help='Classification method.')
    parser.add_argument('--classifier-file', '-cf', type=str, default=CLASSIFIER_FILE,
                        help='Path to the classifier rules file.')
    args = parser.parse_args()

    FORMAT = args.format.split(',')
    transactions = []

    try:
        with open(args.filepath, 'r') as f:
            reader = csv.DictReader(f, fieldnames=FORMAT)
            for row in reader:
                transactions.append(Transaction(**row))
    except Exception as e:
        logger.error(f"{Fore.RED}Failed to read CSV file: {e}{Fore.RESET}")
        sys.exit(1)

    if args.classifier == 'normal':
        for transaction in transactions:
            transaction.class_name = classify(transaction)

    # Calculate statistics
    stats = {}
    for class_name in STATIC_CLASSES:
        amounts = [float(t.amount) for t in transactions if t.class_name == class_name]
        if amounts:
            stats[class_name] = {
                'sum': sum(amounts),
                'avg': mean(amounts),
                'median': median(amounts),
                'std_dev': stdev(amounts)
            }

    # Display statistics
    table_data = [['Class', 'Sum', 'Average', 'Median', 'Standard Deviation']]
    for class_name, data in stats.items():
        table_data.append([class_name, data['sum'], data['avg'], data['median'], data['std_dev']])
    print(tabulate(table_data, headers='firstrow'))

    # Optionally append to stat_log.md
    choice = input('Would you like to write these stats to stat_log.md? (y/n/q): ')
    if choice.lower() == 'y':
        try:
            with open('stat_log.md', 'a') as f:
                f.write('\n---\n')
                f.write(tabulate(table_data, headers='firstrow', tablefmt='pipe'))
                f.write('\n')
        except Exception as e:
            logger.error(f"{Fore.RED}Failed to write to stat_log.md: {e}{Fore.RESET}")


if __name__ == '__main__':
    # Start the loading spinner
    global stop_spinner
    stop_spinner = False
    spinner_thread = threading.Thread(target=loading_spinner)
    spinner_thread.start()

    try:
        main()
    except Exception as e:
        logger.critical(f"{Fore.RED}Fatal error encountered: {e}{Fore.RESET}")
    finally:
        # Stop the loading spinner
        stop_spinner = True
        spinner_thread.join()
