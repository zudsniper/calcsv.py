#!/usr/bin/env python3
# v0.4.4-failed
import os
# import requests
# import shutil
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

# WOW!
# this was a massive waste of time!!!!
# ======================================================================================================================
# def load_figfont():
#     """
#     Load the nvscript figfont.
#     If it doesn't exist, download it.
#     """
#     resources_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')
#     font_path = os.path.join(resources_dir, 'nvscript.flf')
#     pyfiglet_fonts_dir = os.path.join(os.path.dirname(os.path.abspath(Figlet.setFont())), 'fonts')
#
#     # Ensure resources directory exists
#     if not os.path.exists(resources_dir):
#         logger.info(f"{Fore.GREEN}Creating resources directory...{Fore.RESET}")
#         os.makedirs(resources_dir)
#
#     # Check if nvscript.flf exists
#     if not os.path.exists(font_path):
#         logger.info(f"{Fore.GREEN}Downloading nvscript.flf font...{Fore.RESET}")
#         url = 'https://github.com/phracker/figlet-fonts/raw/master/nvscript.flf'
#         response = requests.get(url)
#         with open(font_path, 'wb') as font_file:
#             font_file.write(response.content)
#
#     # Ensure the font file is readable
#     if not os.access(font_path, os.R_OK):
#         logger.warning(f"{Fore.YELLOW}nvscript.flf is not readable. Attempting to change permissions...{Fore.RESET}")
#         try:
#             os.chmod(font_path, 0o644)
#         except PermissionError:
#             logger.error(
#                 f"{Fore.RED}Failed to set read permissions for nvscript.flf. Please run with sudo or set permissions manually.{Fore.RESET}")
#             sys.exit(1)
#
#     # Move the font to pyfiglet's fonts directory
#     shutil.copy2(font_path, pyfiglet_fonts_dir)
#
#     return 'nvscript'  # Return the font name instead of the path
# ======================================================================================================================

# Display startup message
def display_startup_message(args, font_name):
    # Display the figfont title
    # font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'nvscript.flf')
    fig = Figlet(font=font_name)
    title = fig.renderText('calcsv.py')
    print(Back.BLACK + Fore.WHITE + title)  # Inverted colors using colorama

    # Display environment variables and CLI flags
    env_vars = {
        'CSV_FORMAT': (CSV_FORMAT, 'default'),
        'DEFAULT_CLASSIFIER': (DEFAULT_CLASSIFIER, 'default'),
        'CLASSIFIER_FILE': (CLASSIFIER_FILE, 'default'),
        'START_DATE': (START_DATE, 'default'),
        'END_DATE': (END_DATE, 'default')
    }

    for key, value in vars(args).items():
        if value:
            env_vars[key.upper()] = (value, 'CLI flag')

    table_data = []
    for key, (value, source) in env_vars.items():
        if source == 'CLI flag':
            table_data.append([key, Fore.YELLOW + Style.BRIGHT + value])  # Bold and yellow
        elif source == '.env':
            table_data.append([key, Fore.WHITE + value])  # White
        else:
            table_data.append([key, value])

    print(tabulate(table_data, headers=['Variable', 'Value']))

    # Display author's information and project link
    print("\nby @zudsniper 🚬")
    print(Fore.BLUE + Style.UNDERLINED + "https://gh.zod.tf/calcsv.py\n")  # Blue and underlined


# Define the dynamic data structure
class Transaction:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# Load configurations from .env
global CSV_FORMAT, DEFAULT_CLASSIFIER, CLASSIFIER_FILE, STATIC_CLASSES, START_DATE, END_DATE
STATIC_CLASSES = None
CSV_FORMAT = config('FORMAT', default="date,amount,*,,description")
CLASSIFIER_FILE = config('CLASSIFIER_FILE', default='static_classes.json')
DEFAULT_CLASSIFIER = config('CLASSIFIER_TYPE', default='normal')
START_DATE = config('START_DATE', default=None)
END_DATE = config('END_DATE', default=None)


# Load static classes
def load_static_classes():
    global STATIC_CLASSES
    try:
        with open(CLASSIFIER_FILE, 'r') as f:
            STATIC_CLASSES = json.load(f)
    except Exception as e:
        logger.error(f"{Fore.RED}Failed to load {CLASSIFIER_FILE}: {e}{Fore.RESET}")
        sys.exit(1)


logger.remove(0)
logger.add(sys.stderr, format="📠 | <green>{time:HH:mm:ss}</green> | [<level>{level}</level>] {message}", level="DEBUG",
           colorize=True)


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


def format_currency(amount):
    if amount < 0:
        return f"-${abs(amount):,.2f}"
    else:
        return f"${amount:,.2f}"


def main():
    # Load the figfont
    # font_name = load_figfont()
    font_name = 'cybermedium'

    global CSV_FORMAT, DEFAULT_CLASSIFIER, CLASSIFIER_FILE, START_DATE, END_DATE

    parser = argparse.ArgumentParser(description='Parse and classify CSV transactions.')
    parser.add_argument('filepath', type=str, help='Path to the CSV file.')
    parser.add_argument('--format', '-f', type=str, default=CSV_FORMAT, help='CSV value format.', dest='csv_format')
    parser.add_argument('--classifier', '-c', choices=['normal', 'ai', 'hybrid'], default=DEFAULT_CLASSIFIER,
                        help='Classification method.')
    parser.add_argument('--classifier-file', '-cf', type=str,
                        default=config('CLASSIFIER_FILE', default=CLASSIFIER_FILE),
                        help='Path to the classifier rules file.')
    parser.add_argument('--timeframe', '-t', nargs='+', help='Timeframe for calculations in the format YYYY-mm-dd.')
    args = parser.parse_args()

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

    # Display the startup message
    display_startup_message(args, font_name)
# ======================================================================================================================

    load_static_classes()

    FORMAT = args.csv_format.split(',')
    transactions = []

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

    tbl_headers = ['Class', 'Sum', 'Average', 'Median', 'Std. Dev.']
    tbl_headers = [f"{Fore.CYAN}{Style.BRIGHT}{h}{Style.RESET_ALL}{Fore.RESET}" for h in tbl_headers]
    table_data = [tbl_headers]

    for class_name, data in stats.items():
        table_data.append(
            [class_name, format_currency(data['sum']), format_currency(data['avg']), format_currency(data['median']),
             format_currency(data['std_dev'])])
    print(tabulate(table_data, headers='firstrow', tablefmt='pretty', stralign='center', numalign='center'))


if __name__ == '__main__':
    main()
