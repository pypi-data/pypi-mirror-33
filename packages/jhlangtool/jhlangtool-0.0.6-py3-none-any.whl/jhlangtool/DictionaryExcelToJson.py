import pandas
import json

path = "dict_output.xlsx"
excelfile = pandas.ExcelFile(path)
data = excelfile.parse(0)

jsonData = {}
for col in range(1, len(data.columns)):
	#lang = data.columns[col].split('.')[0]
	lang = data.columns[col]
	print(col, lang)
	jsonData['en_'+lang] = {}
	langkey = 'en_'+lang
	for row in range(1, data.shape[0]):
		value = data.iat[row, col]
		key = data.iat[row, 0]
		if str(value) != 'nan':
			jsonData[langkey][key] = value

to_write = open("output_json.json", mode='w', encoding='utf-8')
json.dump(jsonData, to_write, ensure_ascii=False, indent=4)