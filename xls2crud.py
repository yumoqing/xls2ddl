import os
import sys
import codecs
import json
from appPublic.dictObject import DictObject
from xlsxData import xlsxFactory
from appPublic.folderUtils import listFile, _mkdir
from appPublic.myTE import MyTemplateEngine
from tmpls import data_browser_tmpl, get_data_tmpl, data_new_tmpl, data_update_tmpl, data_delete_tmpl

"""
usage:
xls2crud.py dbname models_dir uidir
"""

def build_dbdesc(models_dir: str) -> dict:
	db_desc = {}
	for f in listFile(models_dir, suffixs=['.xlsx']):
		x = xlsxFactory(f)
		d = x.get_data()
		tbname = d.summary[0].name
		db_desc.update({tbname:d})
	return db_desc

def build_crud_ui(crud_data: dict, dbdesc: dict):
	uidir = crud_data.output_dir
	desc = dbdesc[crud_data.tblname]
	desc.update(crud_data.params)
	desc.update({
		"tblname":crud_data.tblname,
		"dbname":crud_data.dbname
	})
	build_table_crud_ui(uidir, desc)

def build_table_crud_ui(uidir: str, desc: dict) -> None:
	_mkdir(uidir)
	build_data_browser(uidir, desc)
	build_data_new(uidir, desc)
	build_data_update(uidir, desc)
	build_data_delete(uidir, desc)
	build_get_data(uidir, desc)

def field_list(desc: dict) -> list:
	fs = []
	for f in desc.fields:
		if desc.codes and f.name in [c.field for c in desc.codes]:
			d = get_code_desc(f, desc)
			fs.append(d)
		else:
			d = setup_ui_info(f)
			fs.append(d)
	return fs

def get_code_desc(field: dict, desc: dict) -> dict:
	d = DictObject(**field.copy())
	if not desc.codes:
		return None
	for c in desc.codes:
		if d.name == c.field:
			d.valueField = d.name
			d.textField = d.name + '_text'
			d.params = {
				'table':c.table,
				'tblvalue':c.valuefield,
				'tbltext':c.textfield,
				'cond':c.cond,
				'valueField':d.valueField,
				'textField':d.textField
			}
			d.dataurl = '/db/get_code.dspy'
			return d
	return None

def setup_ui_info(field:dict) ->dict:
	d = DictObject(**field.copy())
	if d.length:
		d.cwidth = d.length if d.length < 18 else 18
		if d.cwidth < 4:
			d.cwidth = 4;
	else:
		d.length = 0

	if d.type == 'date':
		d.uitype = 'date'
		d.length = 0
	elif d.type == 'time':
		d.uitype = 'time'
		d.length = 0
	elif d.type in ['int', 'short', 'long', 'longlong']:
		d.uitype = 'int'
		d.length = 0
	elif d.type in ['float', 'double', 'decimal']:
		d.uitype = 'float'
	else:
		if d.name.endswith('_date') or d.name.endswith('_dat'):
			d.uitype = 'date'
			d.length = 0
		elif d.name in ['password', 'passwd']:
			d.uitype = 'password'
		else:
			d.uitype = 'str'
	d.datatype = d.type
	d.label = d.title or d.name
	return d

def construct_get_data_sql(desc: dict) -> str:
	shortnames = [c for c in 'bcdefghjklmnopqrstuvwxyz']
	infos = []
	if not desc.codes:
		return f"select * from {desc.summary[0].name}"

	for i, c in enumerate(desc.codes):
		shortname = shortnames[i]
		cond = '1 = 1'
		if c.cond:
			cond = c.cond
		csql = f"""(select {c.valuefield} as {c.field}, 
			{c.textfield} as {c.field}_text from {c.table} where {cond})"""
		infos.append([shortname, f'{shortname}.{c.field}_text', csql, f"a.{c.field} = {shortname}.{c.valuefield}"])
	if len(infos) == 0:
		return f"select * from {desc.summary[0].name}"
	infos.append(['a', 'a.*', desc.summary[0].name, None]) 
	fields = ', '.join([i[1] for i in infos])
	tables = ', '.join([i[2] + ' ' + i[0] for i in infos])
	conds = ' and '.join([i[3] for i in infos if i[3] is not None])
	return f"""select {fields}
from {tables}
where {conds}"""

	if len(addonfields) > 0:
		addonfields = ', ' + addonfields
	
def build_data_browser(pat: str, desc: dict):
	desc = desc.copy()
	desc.fieldlist = field_list(desc)
	e = MyTemplateEngine([])
	s = e.renders(data_browser_tmpl, desc)
	with open(os.path.join(pat, f'index.ui'), 'w') as f:
		f.write(s)

def build_data_new(pat: str, desc: dict):
	e = MyTemplateEngine([])
	desc = desc.copy()
	s = e.renders(data_new_tmpl, desc)
	with open(os.path.join(pat, f'add_{desc.tblname}.dspy'), 'w') as f:
		f.write(s)

def build_data_update(pat: str, desc: dict):
	e = MyTemplateEngine([])
	desc = desc.copy()
	s = e.renders(data_update_tmpl, desc)
	with open(os.path.join(pat, f'update_{desc.tblname}.dspy'), 'w') as f:
		f.write(s)

def build_data_delete(pat: str, desc: dict):
	e = MyTemplateEngine([])
	desc = desc.copy()
	s = e.renders(data_delete_tmpl, desc)
	with open(os.path.join(pat, f'delete_{desc.tblname}.dspy'), 'w') as f:
		f.write(s)

def build_get_data(pat: str, desc: dict):
	e = MyTemplateEngine([])
	desc = desc.copy()
	desc.sql = construct_get_data_sql(desc)
	s = e.renders(get_data_tmpl, desc)
	with open(os.path.join(pat, f'get_{desc.tblname}.dspy'), 'w') as f:
		f.write(s)

if __name__ == '__main__':
	"""
	crud_json has following format
	{
		"models_dir",
		"output_dir",
		"dbname",
		"tblname",
		"params"
	}
	"""
	if len(sys.argv) < 2:
		print(f'{sys.argv} crud_json')
		sys.exit(1)
	crud_data = {}
	with codecs.open(sys.argv[1], 'r', 'utf-8') as f:
		crud_data = DictObject(**json.load(f))
	models_dir = crud_data.models_dir
	ui_dir = crud_data.output_dir
	dbname = crud_data.dbname
	dbdesc = build_dbdesc(models_dir)
	build_crud_ui(crud_data, dbdesc)

