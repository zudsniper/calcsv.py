# `CALCSV.py` 📠  
<sup><i>created by <a target="_blank" alt="author, zudsniper" href="https://gh.zod.tf"><code>@zudsniper</code></a> with various LLM & Chat Agent Models</i></sup>

## NAME
**`calcsv.py`** - Classify and analyze CSV transactions.

## TODO
- [ ] Fix the MarkDown table formatting for `stat_log.md`
- [ ] Add more classifiers (AI, Hybrid)
- [ ] Support 'export to Google Sheets, Excel'
- [ ] **Sort transactions by amount, date** ⭐
  - [ ] Add `--sort|-s <date|amount> <+->` flag to specify sort order & direction
- [ ] Add _'learning'_ mode to allow user to classify transactions and save to `static_classes.json`
- [ ] Add _'interactive'_ mode to allow user to classify transactions and save to `static_classes.json`
  - [ ] Add `-y` flag to skip all interactivity


- [ ] **_GENERATE A BUDGET FROM TRANSACTION STATISTICAL ANALYSIS & GUIDED USER INPUT WORKFLOW_** ⭐⭐⭐

## SYNOPSIS

```shell
python calcsv.py <filepath> [-f <format> | --format <format>] [-c <classifier> | --classifier <classifier>]
```

## DESCRIPTION
**`calcsv.py`** is a tool to parse, classify, and analyze transactions from a CSV file. It supports various CSV formats and classification methods.

## OPTIONS
- **`filepath`**  
  Path to the CSV file. (Required)

- **`-f`, `--format`** *format*  
  Specifies the format of the CSV file. Default is "date,amount,*,,description".

- **`-c`, `--classifier`** *classifier*  
  Specifies the classification method. Choices are "normal", "ai", and "hybrid". Default is "normal".

## USAGE
1. **Default Usage**  
   ```shell
   python calcsv.py transactions.csv
   ```

2. **Specify CSV Format**  
   ```shell
   python calcsv.py transactions.csv --format "date,amount,description"
   ```

3. **Using AI Classifier**  
   ```shell
   python calcsv.py transactions.csv --classifier ai
   ```

## FILES
- **`static_classes.json`**  
  JSON file containing static classification rules.

- **`stat_log.md`**  
  Markdown file where statistics are optionally appended.

## BUILD

<details><summary><code>Click if you want to BUILD!!</code></summary>

### **Prerequisites**
- Python 3.9 or higher
- Git CLI
- Virtualenv
- pipreqs

### **WSL on Windows**
1. Install [WSL](https://docs.microsoft.com/en-us/windows/wsl/install).
2. Open WSL terminal.
3. Clone the repository:  
   ```shell
   git clone https://gh.zod.tf/pybudget2
   ```
4. Navigate to the directory:  
   ```shell
   cd pybudget2
   ```
5. Install requirements:  
   ```shell
   pip install -r requirements.txt
   ```

### **MacOS**
1. Open Terminal.
2. Clone the repository:  
   ```shell
   git clone https://gh.zod.tf/pybudget2
   ```
3. Navigate to the directory:  
   ```shell
   cd pybudget2
   ```
4. Install requirements:  
   ```shell
   pip install -r requirements.txt
   ```

### **Ubuntu/Debian Linux**
1. Open Terminal.
2. Clone the repository:  
   ```shell
   git clone https://gh.zod.tf/pybudget2
   ```
3. Navigate to the directory:  
   ```shell
   cd pybudget2
   ```
4. Install requirements:  
   ```shell
   pip install -r requirements.txt
   ```

### **Windows**
```
+----------------+
|                |
|     WINDOW     |
|                |
+----------------+
```
*For Windows users, it's recommended to use WSL.*

</details>

## ROADMAP
- **AI Classifier**: Implement a machine learning model to classify transactions based on patterns and historical data.
- **Hybrid Classifier**: Combine the rules-based approach of the "normal" classifier with the predictive power of the AI classifier to achieve more accurate classifications.
- **Enhanced UI**: Develop a graphical user interface for easier interaction and visualization of transaction data.
- **Integration with Financial Platforms**: Allow direct import of transaction data from popular financial platforms and banks.

## AUTHOR
Written by [@zudsniper](https://gh.zod.tf).

## REPORTING BUGS
Report bugs to <me@zod.tf>.

## COPYRIGHT
Copyright © 2023 Jason McElhenney. All rights reserved.
