import xlsxwriter
import json
from os import listdir, getcwd
from os.path import basename, join

path = "../../jhipster-dictionary.json"
file = open(path, encoding='utf-8')
data = json.loads(file.read())

print(data.keys())

written_en = False
row_en = 1
excelfile = xlsxwriter.Workbook("dict_output.xlsx")
worksheet = excelfile.add_worksheet(basename("jhipster-dictionary.json"))
col = 0
appeared = {}
for key in data.keys():
	lang1, lang2 = key.split('_')
	col += 1
	row = 1
	worksheet.write(1, col, lang2)
	if written_en:
		for k, v in data[key].items():
			row += 1
			if not (k in appeared.keys()):
				row_en += 1
				appeared[k] = row_en
				worksheet.write(row_en, col, v)
				worksheet.write(row_en, 0, k)
				#row -= 1
				#worksheet.write(row_en+1, col, v)
				#row_en += 1
				#row -= 1
			else:
				worksheet.write(appeared[k], col, v)
			
	else:
		worksheet.write(1, 0, "key")
		for k, v in data[key].items():
			row += 1
			worksheet.write(row, 0, k)
			worksheet.write(row, col, v)
			appeared[k] = row
		written_en = True
		row_en = row

excelfile.close()
