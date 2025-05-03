from openpyxl import Workbook

wb = Workbook()

ws = wb.active

ws['A1'] = "Nom"
ws['B1'] = "Âge"
ws.append(["Alice", 25])
ws.append(["Bob", 30])

wb.save("mon_fichier.xlsx")