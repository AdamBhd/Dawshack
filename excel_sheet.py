from openpyxl import Workbook
import openpyxl
from openpyxl.styles import PatternFill
import os
from datetime import datetime
import transaction

income_col = 'A'
expense_col = 'C'

access_token = transaction.get_access_token()
transactionList = transaction.get_transactions(access_token)

def create_finance_sheet(ws):
    # Define three colors using PatternFill
    income_fill = PatternFill(start_color="98FB98", end_color="98FB98", fill_type="solid")  # Pale Green
    expenses_fill = PatternFill(start_color="FFC0CB", end_color="FFC0CB", fill_type="solid")  # Light Pink
    difference_fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")  # Light Blue

    # Category headers
    ws[f'{income_col}1'] = "Income"
    ws[f'{expense_col}1'] = "Expenses"
    ws['E1'] = "Difference"

    # Apply the fill colors to the headers
    ws[f'{income_col}1'].fill = income_fill
    ws[f'{expense_col}1'].fill = expenses_fill
    ws['E1'].fill = difference_fill

def find_next_empty_row(ws, column):
    row = 2  
    while ws[f'{column}{row}'].value is not None:
        row += 1
    return row

def create_sheet(wb):
    current_date = datetime.now().strftime("%Y-%m")
    wb.create_sheet(title=current_date)

def add_income(ws, amount):
    next_row = find_next_empty_row(ws, income_col)
    ws[f'{income_col}{next_row}'] = amount

def add_expense(ws, amount):
    next_row = find_next_empty_row(ws, expense_col)
    ws[f'{expense_col}{next_row}'] = amount

#main
if os.path.exists("BMS_finances.xlsx"):
    wb = openpyxl.load_workbook("BMS_finances.xlsx")
else:
    wb = Workbook()
    if "Sheet" in wb.sheetnames:
        del wb["Sheet"]

sheet_name = datetime.now().strftime("%Y-%m")
if sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
else:
    ws = wb.create_sheet(title=sheet_name)
    create_finance_sheet(ws)

total_income = sum(cell.value for cell in ws[income_col][1:] if cell.value is not None)
total_expenses = sum(cell.value for cell in ws[expense_col][1:] if cell.value is not None)
difference = total_income - total_expenses

ws['E2'] = f"{'+' if difference >= 0 else '-'}{abs(difference)}"

print(transactionList)

wb.save("BMS_finances.xlsx")
