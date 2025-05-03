from openpyxl import Workbook
import openpyxl
from openpyxl.styles import PatternFill
import os
from datetime import datetime

income_col = 'A'
expense_col = 'C'

def create_finance_sheet(ws):
    # Define three colors using PatternFill
    income_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")  # Yellow
    expenses_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")  # Red
    difference_fill = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")  # Green

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

wb.save("BMS_finances.xlsx")
