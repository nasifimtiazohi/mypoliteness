import openpyxl
wb=openpyxl.load_workbook('politeResult.xlsx')
ws=wb.get_active_sheet()
ws['A1']="bainchod"
wb.save('politeResult.xlsx')
