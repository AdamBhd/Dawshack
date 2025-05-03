#  Student Budget Tracker

This project is a simple financial automation tool designed to help students manage their budget more easily by automatically classifying expenses.

##  Why?

Many students struggle with financial insecurity and have limited time to manage their spending. This app connects to a mock banking interface (using the Plaid sandbox) and tracks expenses, automatically classifying them into an Excel file. It’s a quick way to gain awareness of your spending habits — without spending hours on budgeting.

##  How to Run

1. Clone the repository and install the required dependencies:

```bash
pip install -r requirements.txt
```
2. Run the app:
```
python main.py
```


An Excel file with classified transactions will be generated after fetching sandbox data.

## Notes
This project uses Plaid's sandbox environment, so no real bank connection is required.

You can simulate transactions via the Plaid Sandbox UI.
