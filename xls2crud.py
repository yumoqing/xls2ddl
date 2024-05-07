import os
import sys
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

def build_crud_ui(uidir: str, dbname, dbdesc):
	for tblname, desc in dbdesc.items():
		build_table_crud_ui(uidir, dbname, tblname, desc)

def build_table_crud_ui(uidir: str, dbname: str, tblname:str, desc: dict):
	pat = os.path.join(uidir, tblname)
	_mkdir(pat)
	build_data_browser(pat, dbname, tblname, desc)
	build_data_new(pat, dbname, tblname, desc)
	build_data_update(pat, dbname, tblname, desc)
	build_data_delete(pat, dbname, tblname, desc)
	build_get_data(pat, dbname, tblname, desc)

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
		if (d.cwidth < 4){
			d.cwidth = 4;
		}
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
	
def build_data_browser(pat: str, dbname:str, tblname: str, desc: dict):
	desc = desc.copy()
	desc.dbname = dbname
	desc.fieldlist = field_list(desc)
	e = MyTemplateEngine([])
	s = e.renders(data_browser_tmpl, desc)
	with open(os.path.join(pat, f'{tblname}.ui'), 'w') as f:
		f.write(s)

def build_data_new(pat: str, dbname:str, tblname: str, desc: dict):
	e = MyTemplateEngine([])
	desc = desc.copy()
	desc.dbname = dbname
	s = e.renders(data_new_tmpl, desc)
	with open(os.path.join(pat, f'add_{tblname}.dspy'), 'w') as f:
		f.write(s)

def build_data_update(pat: str, dbname:str, tblname: str, desc: dict):
	e = MyTemplateEngine([])
	desc = desc.copy()
	desc.dbname = dbname
	s = e.renders(data_update_tmpl, desc)
	with open(os.path.join(pat, f'update_{tblname}.dspy'), 'w') as f:
		f.write(s)

def build_data_delete(pat: str, dbname:str, tblname: str, desc: dict):
	e = MyTemplateEngine([])
	desc = desc.copy()
	desc.dbname = dbname
	s = e.renders(data_delete_tmpl, desc)
	with open(os.path.join(pat, f'delete_{tblname}.dspy'), 'w') as f:
		f.write(s)

def build_get_data(pat: str, dbname:str, tblname: str, desc: dict):
	e = MyTemplateEngine([])
	desc = desc.copy()
	desc.dbname = dbname
	desc.sql = construct_get_data_sql(desc)
	s = e.renders(get_data_tmpl, desc)
	with open(os.path.join(pat, f'get_{tblname}.dspy'), 'w') as f:
		f.write(s)

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print(f'{sys.argv} models_dir created_ui')
		sys.exit(1)
	
	models_dir = sys.argv[1]
	ui_dir = sys.argv[2]
	dbdesc = build_dbdesc(models_dir)
	build_crud_ui(ui_dir, 'kboss', dbdesc)

