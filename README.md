# CSV TRANSACTION CLASSIFIER(1) - Manual Page

## NAME
**csv_transaction_classifier** - Classify and analyze CSV transactions.

## SYNOPSIS

```shell
python calcsv.py <filepath> [-f <format> | --format <format>] [-c <classifier> | --classifier <classifier>]
```

## DESCRIPTION
**csv_transaction_classifier** is a tool to parse, classify, and analyze transactions from a CSV file. It supports various CSV formats and classification methods.

## OPTIONS
- **`filepath`**  
  Path to the CSV file. (Required)

- **`-f`, `--format`** *format*  
  Specifies the format of the CSV file. Default is "date,amount,,,description".

- **`-c`, `--classifier`** *classifier*  
  Specifies the classification method. Choices are "normal", "ai", and "hybrid". Default is "normal".

## FILES
- **`static_classes.json`**  
  JSON file containing static classification rules.

- **`stat_log.md`**  
  Markdown file where statistics are optionally appended.

## AUTHOR
Written by [@zudsniper](https://gh.zod.tf).

## REPORTING BUGS
Report bugs to <me@zod.tf>.

## COPYRIGHT
Copyright © 2023 Jason McElhenney. All rights reserved.
