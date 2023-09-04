#!/usr/bin/env python3
# v0.4.0
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
global CSV_FORMAT, DEFAULT_CLASSIFIER, CLASSIFIER_FILE, STATIC_CLASSES
STATIC_CLASSES = None
CSV_FORMAT = config('FORMAT', default="date,amount,*,,description")
CLASSIFIER_FILE = config('CLASSIFIER_FILE', default='static_classes.json')
DEFAULT_CLASSIFIER = config('CLASSIFIER_TYPE', default='normal')


# Load static classes
def load_static_classes():
    global STATIC_CLASSES
    try:
        with open(CLASSIFIER_FILE, 'r') as f:
            STATIC_CLASSES = json.load(f)
    except Exception as e:
        logger.error(f"{Fore.RED}Failed to load {CLASSIFIER_FILE}: {e}{Fore.RESET}")
        sys.exit(1)


# Remove default logger
logger.remove(0)

# Modify logger to be pretty
logger.add(sys.stderr, format="📠 | <green>{time:HH:mm:ss}</green> | [<level>{level}</level>] {message}", level="DEBUG",
           colorize=True)


# def custom_format(record):
#     format_str = "{time:HH:mm:ss} | <level>{level}</level> | {message} "
#     if record["level"].name in ["ERROR", "CRITICAL"]:
#         format_str += " | {name}:{function}:{line}"
#     return format_str
#

# logger.add(sys.stderr, format=custom_format, filter="my_module", level="INFO", colorize=True)


# classify transactions using the consecutive substrings listed in static_classes.json -- for `normal` classifier
def classify(transaction):
    global STATIC_CLASSES
    description = getattr(transaction, "description", "").lower()  # Ensure the description attribute exists
    for class_name, keywords in STATIC_CLASSES.items():
        for keyword in keywords:
            if keyword.lower() in description:
                logger.debug(f"Transaction '{description}' matched keyword '{keyword}' for class '{class_name}'.")
                return class_name
    logger.debug(f"Transaction '{description}' did not match any keyword.")
    return None


# Loading spinner (silly rainbow) to show that the program is still running
def loading_spinner():
    emojis = ["🔴", "🟠", "🟡", "🟢", "🔵", "🟣", "🟤"]
    idx = 0
    while not stop_spinner:
        print(f"\r{emojis[idx % len(emojis)]} Processing...", end="")
        idx += 1
        time.sleep(0.2)


# a helper function to identify the problematic portion of a row when reading in CSV lines
def identify_problematic_portion(row):
    for key, value in row.items():
        if not isinstance(key, str):
            return f"Key: {key}, Value: {value}"
    return "Unknown issue"


# show currency in a pretty format
def format_currency(amount):
    if amount < 0:
        return f"-${abs(amount):,.2f}"
    else:
        return f"${amount:,.2f}"


def main():
    global CSV_FORMAT, DEFAULT_CLASSIFIER, CLASSIFIER_FILE

    parser = argparse.ArgumentParser(description='Parse and classify CSV transactions.')
    parser.add_argument('filepath', type=str, help='Path to the CSV file.')
    parser.add_argument('--format', '-f', type=str, default=CSV_FORMAT, help='CSV value format.', dest='csv_format')
    parser.add_argument('--classifier', '-c', choices=['normal', 'ai', 'hybrid'], default=DEFAULT_CLASSIFIER,
                        help='Classification method.')
    parser.add_argument('--classifier-file', '-cf', type=str,
                        default=config('CLASSIFIER_FILE', default=CLASSIFIER_FILE),
                        help='Path to the classifier rules file.')
    args = parser.parse_args()

    # Override .env settings with CLI flags if they are provided
    if args.csv_format:
        CSV_FORMAT = args.csv_format
    if args.classifier:
        DEFAULT_CLASSIFIER = args.classifier
    if args.classifier_file:
        CLASSIFIER_FILE = args.classifier_file

    # Load static classes
    load_static_classes()

    FORMAT = args.csv_format.split(',')
    transactions = []

    try:
        with open(args.filepath, 'r') as f:
            reader = csv.DictReader(f, fieldnames=FORMAT)
            for row in reader:
                try:
                    transactions.append(Transaction(**row))
                except TypeError:
                    logger.error(f"{Fore.RED}Offending CSV line: {','.join(row.values())}{Fore.RESET}")
                    # Additional logic to highlight the problematic portion
                    problematic_portion = identify_problematic_portion(row)
                    logger.error(f"{Fore.RED}Problematic portion: {problematic_portion}{Fore.RESET}")
                    sys.exit(1)
    except Exception as e:
        logger.error(f"{Fore.RED}Failed to read CSV file: {e}{Fore.RESET}")
        sys.exit(1)

    # Classify transactions
    # normal mode
    if args.classifier == 'normal':
        for transaction in transactions:
            transaction.class_name = classify(transaction)

    global STATIC_CLASSES
    # Calculate statistics
    stats = {}
    for class_name in STATIC_CLASSES:
        amounts = []
        for t in transactions:
            if not t.class_name:
                logger.warning(
                    f"{Fore.YELLOW}Transaction '{t.description if t.description else ''}' was not classified.{Fore.RESET}")
                continue
            if t.class_name == class_name:
                amounts.append(float(t.amount))
        if amounts:
            stats[class_name] = {
                'sum': sum(amounts),
                'avg': mean(amounts),
                'median': median(amounts),
                'std_dev': stdev(amounts) if len(amounts) > 1 else 0
            }

    # Display statistics
        # headers
        tbl_headers = ['Class', 'Sum', 'Average', 'Median', 'Std. Dev.']
        tbl_headers = [f"{Fore.CYAN}{Style.BRIGHT}{h}{Style.RESET_ALL}{Fore.RESET}" for h in tbl_headers]
    table_data = [tbl_headers]

    for class_name, data in stats.items():
        table_data.append(
            [class_name, format_currency(data['sum']), format_currency(data['avg']), format_currency(data['median']),
             format_currency(data['std_dev'])])
    print(tabulate(table_data, headers='firstrow', tablefmt='pretty', stralign='center', numalign='center'))

    # TODO: Fix this... it doesn't output markdown, it looks really really bad
    # Optionally append to stat_log.md
    choice = input(f"Would you like to write these stats to stat_log.md? {Style.BRIGHT}(y/n/q){Style.RESET_ALL}: ")
    if choice.lower() == 'y':
        try:
            with open('stat_log.md', 'a') as f:
                f.write('\n---\n')
                f.write(tabulate(table_data, headers='firstrow', tablefmt='simple-outline'))
                f.write('\n')
        except Exception as e:
            logger.error(f"{Fore.RED}Failed to write to stat_log.md: {e}{Fore.RESET}")


if __name__ == '__main__':
    # Start the loading spinner
    # global stop_spinner
    stop_spinner = False
    # spinner_thread = threading.Thread(target=loading_spinner)
    # spinner_thread.start()

    try:
        main()
    except Exception as e:
        logger.critical(f"{Fore.WHITE}{Style.BRIGHT}Fatal error encountered! \n{Style.RESET_ALL}{e}{Fore.RESET}")
        # logger.debug(f"{Fore.WHITE}{Back.LIGHTRED_EX}{Style.BRIGHT}TRACEBACK\n{Style.RESET_ALL}{e.with_traceback()}{Fore.RESET}")

    finally:
        # Stop the loading spinner
        stop_spinner = True
        # spinner_thread.join()
