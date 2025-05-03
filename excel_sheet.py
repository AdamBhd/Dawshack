from openpyxl import Workbook
import openpyxl
from openpyxl.styles import PatternFill
from openpyxl import Workbook, load_workbook
import os
from datetime import datetime
import transaction
import const
import win32com.client
import pythoncom
income_col = 'B'
expense_name_col = 'B'
category_col = 'C'
amount_col = 'D'

transactionList = transaction.get_transactions(transaction.initialize_transaction())

def close_excel_file():
    try:
        pythoncom.CoInitialize()
        excel = win32com.client.GetActiveObject("Excel.Application")
        for wb in excel.Workbooks:
            if wb.FullName.lower() == os.path.abspath(const.FILE_NAME).lower():
                wb.Close(SaveChanges=True)
                print(f"Closed Excel file: {const.FILE_NAME}")
                break
        if excel.Workbooks.Count == 0:
            excel.Quit()
    except Exception as e:
        print("Excel not open or error closing:", e)

def create_finance_sheet(ws):
    if not os.path.exists(const.FILE_NAME):
        wb = Workbook()
        ws = wb.active
        ws.title = "BMS_finances"
        ws.append(["Date", "Name", "Amount", "Category"])
    else:
        wb = load_workbook(const.FILE_NAME)
        ws = wb["BMS_finances"]
    

def find_next_empty_row(ws, column):
    row = 2  
    while ws[f'{column}{row}'].value is not None:
        row += 1
    return row

def create_sheet(wb):
    current_date = datetime.now().strftime("%Y-%m")
    wb.create_sheet(title=current_date)

def add_income(ws, amount):
    
    ws[f'{income_col}{3}'] += amount

def add_expense(ws, amount, expense_name, category):
    next_row = find_next_empty_row(ws, income_col)
    ws[f'{expense_name_col}{next_row}'] = expense_name
    ws[f'{category_col}{next_row}'] = category
    ws[f'{amount_col}{next_row}'] = amount


if os.path.exists(const.FILE_NAME):
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
for transaction in transactionList:
    print(f"Date: {transaction['date']}, amount: {transaction['amount']}, Description: {transaction['name']}, Category: {transaction['category']}")

wb.save("BMS_finances.xlsx")
