#!/usr/bin/env python3
# v0.5.1
import os
import argparse
import csv
import json
import signal
import sys
from statistics import mean, median, stdev
from colorama import init, Fore, Back, Style
from loguru import logger
from pyfiglet import Figlet
from tabulate import tabulate
from decouple import config
from datetime import datetime

# Initialize colorama
init(autoreset=True)


# Display startup message
def display_startup_message(args, font_name):
    # Display the figfont title
    fig = Figlet(font=font_name)
    title = fig.renderText('CalCSV')
    title_length = len(title[0:title.find('\n')])
    title = os.linesep.join([s for s in title.splitlines() if s]) # remove empty lines
    print('=' * title_length + Fore.RESET + Back.RESET + "\n\n\n") # TODO: figure out why the fuck there are 3 newlines after the figfont
    print(Back.BLACK + Fore.WHITE + title)
    print('=' * title_length + Fore.RESET + Back.RESET)
    # Display environment variables and CLI flags
    env_vars = {
        'CSV_FORMAT': (CSV_FORMAT, 'default'),
        'DEFAULT_CLASSIFIER': (DEFAULT_CLASSIFIER, 'default'),
        'CLASSIFIER_FILE': (CLASSIFIER_FILE, 'default'),
        'START_DATE': (START_DATE, 'default'),
        'END_DATE': (END_DATE, 'default')
    }

    for key, value in vars(args).items():
        if key:
            env_vars[key.upper()] = (value, 'CLI flag')

    table_data = []
    for key, (value, source) in env_vars.items():
        # Convert value to string if it's a list
        value_str = ', '.join(value) if isinstance(value, list) else str(value)

        if source == 'CLI flag':
            table_data.append([key, Fore.YELLOW + Style.BRIGHT + value_str + Style.RESET_ALL])  # Bold and yellow
        elif source == '.env':
            table_data.append([key, Fore.WHITE + value_str + Style.RESET_ALL])  # White
        else:
            table_data.append([key, value_str])

    print(tabulate(table_data, headers=['Variable', 'Value']))

    # Display author's information and project link
    print("\nby @zudsniper 🚬")
    print(Fore.BLUE + Style.BRIGHT + "https://gh.zod.tf/calcsv.py\n")  # Blue and underlined


# Define the dynamic data structure
class Transaction:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# Load configurations from .env
global CSV_FORMAT, DEFAULT_CLASSIFIER, CLASSIFIER_FILE, STATIC_CLASSES, START_DATE, END_DATE, LOG_LEVEL
STATIC_CLASSES = None
CSV_FORMAT = config('FORMAT', default="date,amount,*,,description")
CLASSIFIER_FILE = config('CLASSIFIER_FILE', default='static_classes.json')
DEFAULT_CLASSIFIER = config('CLASSIFIER_TYPE', default='normal')
START_DATE = config('START_DATE', default=None)
END_DATE = config('END_DATE', default=None)
LOG_LEVEL = config('LOG_LEVEL', default='INFO')


# Load static classes
def load_static_classes():
    global STATIC_CLASSES
    try:
        with open(CLASSIFIER_FILE, 'r') as f:
            STATIC_CLASSES = json.load(f)
    except Exception as e:
        logger.error(f"{Fore.RED}Failed to load {CLASSIFIER_FILE}: {e}{Fore.RESET}")
        sys.exit(1)


def classify(transaction):
    global STATIC_CLASSES
    description = getattr(transaction, "description", "").lower()
    for class_name, keywords in STATIC_CLASSES.items():
        for keyword in keywords:
            if keyword.lower() in description:
                logger.debug(f"Transaction '{description}' matched keyword '{keyword}' for class '{class_name}'.")
                return class_name
    logger.debug(f"Transaction '{description}' did not match any keyword.")
    return 'Uncategorized'


def signal_handler(sig, frame):
    logger.error(
        f"{Fore.RED}You made me stop! Here are all the settings that might be useful for debugging:{Fore.RESET}")
    logger.error(f"CSV_FORMAT: {CSV_FORMAT}")
    logger.error(f"DEFAULT_CLASSIFIER: {DEFAULT_CLASSIFIER}")
    logger.error(f"CLASSIFIER_FILE: {CLASSIFIER_FILE}")
    logger.error(f"START_DATE: {START_DATE}")
    logger.error(f"END_DATE: {END_DATE}")
    sys.exit(1)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# format numbers as currency, handling negative values
def format_currency(amount):
    if amount < 0:
        return f"-${abs(amount):,.2f}"
    else:
        return f"${amount:,.2f}"


def main():
    # ======================================================================================================================
    font_name = 'roman'

    global CSV_FORMAT, DEFAULT_CLASSIFIER, CLASSIFIER_FILE, START_DATE, END_DATE

    # Parse CLI arguments
    parser = argparse.ArgumentParser(description='Parse and classify CSV transactions.')
    parser.add_argument('filepath', type=str, help='Path to the CSV file.')
    parser.add_argument('--format', '-f', type=str, default=CSV_FORMAT, help='CSV value format.', dest='csv_format')
    parser.add_argument('--classifier', '-c', choices=['normal', 'ai', 'hybrid'], default=DEFAULT_CLASSIFIER,
                        help='Classification method.')
    parser.add_argument('--classifier-file', '-cf', type=str,
                        default=config('CLASSIFIER_FILE', default=CLASSIFIER_FILE),
                        help='Path to the classifier rules file.')
    parser.add_argument('--timeframe', '-t', nargs='+', help='Timeframe for calculations in the format YYYY-mm-dd.')
    parser.add_argument('--log_level', '-l', type=str, default=LOG_LEVEL,  # Added this line for the log level
                        help='Log level for the logger.', dest='log_level')
    args = parser.parse_args()

    # Override the default values with the CLI arguments
    if args.csv_format:
        CSV_FORMAT = args.csv_format
    if args.classifier:
        DEFAULT_CLASSIFIER = args.classifier
    if args.classifier_file:
        CLASSIFIER_FILE = args.classifier_file
    if args.timeframe:
        START_DATE = args.timeframe[0]
        if len(args.timeframe) > 1:
            END_DATE = args.timeframe[1]
        else:
            END_DATE = datetime.now().strftime('%Y-%m-%d')

    # Adjusting the logger's level based on the CLI argument or environment variable
    logger.remove(0)
    logger.add(sys.stderr, format="📠 | <green>{time:HH:mm:ss}</green> | [<level>{level}</level>] {message}",
               level=args.log_level,
               colorize=True)

    # Display the startup message
    display_startup_message(args, font_name)
    # ======================================================================================================================

    # Load static classes
    load_static_classes()

    # Parse the CSV file
    FORMAT = args.csv_format.split(',')
    transactions = []

    logger.info(f"Reading CSV file '{args.filepath}'...")


    try:
        with open(args.filepath, 'r') as f:
            reader = csv.DictReader(f, fieldnames=FORMAT)
            for row in reader:
                try:
                    # Adjusting the date format to handle 'MM/DD/YYYY'
                    transaction_date = datetime.strptime(row['date'], '%m/%d/%Y').date()
                    if START_DATE and END_DATE:
                        start_date = datetime.strptime(START_DATE, '%Y-%m-%d').date()
                        end_date = datetime.strptime(END_DATE, '%Y-%m-%d').date()
                        if start_date <= transaction_date <= end_date:
                            transactions.append(Transaction(**row))
                    else:
                        transactions.append(Transaction(**row))
                except TypeError:
                    logger.error(f"{Fore.RED}Offending CSV line: {','.join(row.values())}{Fore.RESET}")
                    sys.exit(1)
    except Exception as e:
        logger.error(f"{Fore.RED}Failed to read CSV file: {e}{Fore.RESET}")
        sys.exit(1)

    logger.info(f"Total {Style.BRIGHT}{Fore.YELLOW}potential{Style.BRIGHT} transactions: " + Fore.BLUE + str(reader.line_num) + Fore.RESET)
    logger.info(f"Total {Style.BRIGHT}{Fore.GREEN}registered{Style.BRIGHT} transactions: " + Fore.BLUE + str(len(transactions)) + Fore.RESET)
    logger.info(f"{Style.BRIGHT}Classifying transactions{Style.RESET_ALL} & {Style.BRIGHT}calculating statistics{Style.RESET_ALL}...")

    if args.classifier == 'normal':
        for transaction in transactions:
            transaction.class_name = classify(transaction)

    global STATIC_CLASSES
    stats = {}
    for class_name in STATIC_CLASSES:
        amounts = []
        for t in transactions:
            if not t.class_name:
                logger.warning(
                    f"{Fore.YELLOW}Transaction '{t.description if t.description else ''}' was placed in the 'Uncategorized' category.{Fore.RESET}")
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

    # Adding statistics for Uncategorized transactions
    uncategorized_amounts = [float(t.amount) for t in transactions if t.class_name == 'Uncategorized']
    if uncategorized_amounts:
        stats['Uncategorized'] = {
            'sum': sum(uncategorized_amounts),
            'avg': mean(uncategorized_amounts),
            'median': median(uncategorized_amounts),
            'std_dev': stdev(uncategorized_amounts) if len(uncategorized_amounts) > 1 else 0
        }

    tbl_headers = ['Class', 'Sum', 'Average', 'Median', 'Std. Dev.']
    tbl_headers = [f"{Fore.CYAN}{Style.BRIGHT}{h}{Style.RESET_ALL}{Fore.RESET}" for h in tbl_headers]
    table_data = [tbl_headers]

    for class_name, data in stats.items():
        table_data.append(
            [class_name, format_currency(data['sum']), format_currency(data['avg']), format_currency(data['median']),
             format_currency(data['std_dev'])])

    # Adding Overall statistics
    all_amounts = [float(t.amount) for t in transactions]
    overall_stats = {
        'sum': sum(all_amounts),
        'avg': mean(all_amounts),
        'median': median(all_amounts),
        'std_dev': stdev(all_amounts) if len(all_amounts) > 1 else 0
    }
    table_data.append(['-' * 20] * 5)  # Separator
    table_data.append(
        ['Overall', format_currency(overall_stats['sum']), format_currency(overall_stats['avg']),
         format_currency(overall_stats['median']), format_currency(overall_stats['std_dev'])])

    # Print the table of statistics as well as the timeframe, if timeframes were specified
    if START_DATE or END_DATE:
        logger.info("TIMEFRAME: " + Fore.BLUE + f"{START_DATE} - {END_DATE}" + Fore.RESET)
    print(tabulate(table_data, headers='firstrow', tablefmt='pretty', stralign='center', numalign='center'))


if __name__ == '__main__':
    main()
