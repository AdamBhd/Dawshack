import tkinter as tk
from tkinter import messagebox
from openpyxl import Workbook, load_workbook
import openpyxl
from openpyxl.utils import get_column_letter
import os
from datetime import datetime
import subprocess
import platform
import const
import excel_sheet

def add_purchase_to_excel():
    name = entry_name.get()
    amount = entry_amount.get()
    category = entry_category.get()
    
    if not name or not amount or not category:
        messagebox.showwarning("Missing Field", "All fields are required.")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number.")
        return

    if os.path.exists(const.FILE_NAME):
        wb = openpyxl.load_workbook(const.FILE_NAME)
    else:
        wb = excel_sheet.create_finance_sheet()
        excel_sheet.add_bank_transaction(wb)

    sheet_name = datetime.now().strftime("%Y-%m") #date transaction
    if sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
    else:
        ws = excel_sheet.create_sheet(wb, sheet_name)

    date = datetime.now().strftime("%Y-%m-%d")
    excel_sheet.add_expense(ws, amount, name, category, date)
    wb.save(const.FILE_NAME)
    
    entry_name.delete(0, tk.END)
    entry_amount.delete(0, tk.END)
    entry_category.delete(0, tk.END)

    messagebox.showinfo("Success", "Purchase recorded!")
excel_sheet.close_excel_file()
root = tk.Tk()
root.title("Purchase Recorder")
root.geometry("300x250")

tk.Label(root, text="Purchase Name").pack(pady=5)
entry_name = tk.Entry(root, width=30)
entry_name.pack()

tk.Label(root, text="Amount ($)").pack(pady=5)
entry_amount = tk.Entry(root, width=30)
entry_amount.pack()

tk.Label(root, text="Category").pack(pady=5)
entry_category = tk.Entry(root, width=30)
entry_category.pack()

tk.Button(root, text="Save Purchase", command=add_purchase_to_excel).pack(pady=20)

root.mainloop()
if platform.system() == "Windows":
    subprocess.Popen(["start", const.FILE_NAME], shell=True)
