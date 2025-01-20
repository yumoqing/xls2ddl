import os
import sys
import codecs
import json
import argparse

from appPublic.dictObject import DictObject
from xlsxData import xlsxFactory
from appPublic.folderUtils import listFile, _mkdir
from appPublic.myTE import MyTemplateEngine
from tmpls import data_browser_tmpl, get_data_tmpl, data_new_tmpl, data_update_tmpl, data_delete_tmpl, check_changed_tmpls
from appPublic.argsConvert import ArgsConvert

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
	tables = [ k for k in dbdesc.keys() ]
	print(f'write to {uidir},{tables=}')
	desc = dbdesc[crud_data.tblname]
	desc.update(crud_data.params)
	if desc.relation:
		desc.checkField = 'has_' + desc.relation.param_field 
		binds = desc.binds or []
		binds.append({
            "wid":"self",
            "event":"row_check_changed",
            "actiontype":"urlwidget",
            "target":"self",
            "options":{
                "params":{},
                "url":"{{entire_url('check_changed.dspy')}}"
            }
        })
		desc.binds = binds
	if crud_data.params.subtables:
		if len(crud_data.params.subtables) == 1:
			t = crud_data.params.subtables[0]
			url = f"../{t.subtable}"
			content_view = DictObject(**{
	            "widgettype":"urlwidget",
				"options":{
					"params":{
						"oops":1,
						f"{t.field}":"${id}"
					},  
					"url":"{{entire_url('" + url + "')}}"
				}   
			})
		else:
			items = []
			for t in crud_data.params.subtables:
				url = f"../{t.subtable}"
				item = {
					"name":t.subtable,
					"label":t.title or t.subtable,
					"content":{
						"widgettype":"urlwidget",
						"options":{
							"params":{
								"oops":1,
								f"{t.field}":"${id}"
							},  
							"url":"{{entire_url('" + url + "')}}"
						}   
					}   
				}
				items.append(item)
			content_view = DictObject(**{
				"widgettype":"TabPanel",
				"options":{
					"tab_wide":"auto",
					"height":"100%",
					"width":"100%",
					"tab_pos":"top",
					"items":items
				}
			})
		desc.content_view = content_view

	desc.update({
		"tblname":crud_data.tblname,
		"dbname":crud_data.dbname
	})
	build_table_crud_ui(uidir, desc)

def build_table_crud_ui(uidir: str, desc: dict) -> None:
	_mkdir(uidir)
	# print('table_desc=', desc)
	build_data_browser(uidir, desc)
	if desc.relation:
		build_check_changed(uidir, desc)
	else:
		build_data_new(uidir, desc)
		build_data_update(uidir, desc)
		build_data_delete(uidir, desc)
	build_get_data(uidir, desc)

def alter_field(field:dict, desc:DictObject) -> dict:
	name = field['name']
	ret = field.copy()
	alters = desc.browserfields.alters
	if alters:
		[ ret.update(alters[k]) for k in alters.keys() if k == name ]
	return ret

def field_list(desc: dict) -> list:
	fs = []
	for f in desc.fields:
		if desc.codes and f.name in [c.field for c in desc.codes]:
			d = get_code_desc(f, desc)
		else:
			d = setup_ui_info(f)
		"""
		use alters to modify fields
		"""
		d = alter_field(d, desc)
		fs.append(d)
	return fs

def get_code_desc(field: dict, desc: dict) -> dict:
	d = DictObject(**field.copy())
	if not desc.codes:
		return None
	for c in desc.codes:
		if d.name == c.field:
			d.label = d.title or d.name
			d.uitype = 'code'
			d.valueField = d.name
			d.textField = d.name + '_text'
			d.params = {
				'dbname':"{{rfexe('get_module_dbname', '" + desc.modulename + "')}}",
				'table':c.table,
				'tblvalue':c.valuefield,
				'tbltext':c.textfield,
				'valueField':d.valueField,
				'textField':d.textField
			}
			if c.cond:
				d.params['cond'] = c.cond
			d.dataurl = "{{entire_url('/get_code.dspy')}}"
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
			if d.type=='str' and d.length > 100:
				d.uitype = 'text'
				d.rows = 4
			else:
				d.uitype = 'str'
	d.datatype = d.type
	d.label = d.title or d.name
	return d

def construct_get_data_sql(desc: dict) -> str:
	shortnames = [c for c in 'bcdefghjklmnopqrstuvwxyz']
	infos = []
	if desc.relation and desc.codes:
		print('============')
		param_field = "${" + desc.relation.param_field + "}$"
		for code in desc.codes:
			if code.field == desc.relation.outter_field:
				return f"""select '$[{desc.relation.param_field}]$' as {desc.relation.param_field}, 
case when b.{desc.relation.param_field} is NULL then 0 else 1 end has_{desc.relation.param_field},
a.{code.valuefield} as {code.field}, 
a.{code.textfield} as {code.field}_text
from {code.table} a left join 
(select * from {desc.tblname} where {desc.relation.param_field} ={param_field}) b 
	on a.{code.valuefield} = b.{code.field}
"""
	else:
		print('===== not ======', desc.relation, 'codes=', desc.codes)
	if not desc.codes or len(desc.codes) == 0:
		return f"select * from {desc.tblname} where 1=1 " + '{}'

	for i, c in enumerate(desc.codes):
		shortname = shortnames[i]
		cond = '1 = 1'
		if c.cond:
			cond = c.cond
		csql = f"""(select {c.valuefield} as {c.field}, 
			{c.textfield} as {c.field}_text from {c.table} where {cond})"""
		infos.append([f'{shortname}.{c.field}_text', f"{csql} {shortname} on a.{c.field} = {shortname}.{c.field}"])
	bt = f'(select * from {desc.summary[0].name} where 1=1' + "{}) a"
	infos.insert(0, ['a.*', bt]) 
	fields = ', '.join([i[0] for i in infos])
	tables = ' left join '.join([i[1] for i in infos])
	return f"""select {fields}
from {tables}"""

	
def build_data_browser(pat: str, desc: dict):
	# print(desc)
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

def build_check_changed(pat:str, desc:dict):
    e = MyTemplateEngine([])
    desc = desc.copy()
    s = e.renders(check_changed_tmpls, desc)
    with open(os.path.join(pat, 'check_changed.dspy'), 'w') as f:
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
	parser = argparse.ArgumentParser('xls2crud')
	parser.add_argument('-m', '--models_dir')
	parser.add_argument('-o', '--output_dir')
	parser.add_argument('modulename')
	parser.add_argument('files', nargs='*')
	args = parser.parse_args()
	if len(args.files) < 1:
		print(f'Usage:\n{sys.argv[0]} [-m models_dir] [-o output_dir] json_file ....\n')
		sys.exit(1)
	print(args)
	ns = {k:v for k, v in os.environ.items()}
	for fn in args.files:
		print(f'handle {fn}')
		crud_data = {}
		with codecs.open(fn, 'r', 'utf-8') as f:
			a = json.load(f)
			ac = ArgsConvert('${','}$')
			a = ac.convert(a,ns)
			crud_data = DictObject(**a)
		if args.models_dir:
			crud_data.models_dir = args.models_dir
		models_dir = crud_data.models_dir
		if args.output_dir:
			crud_data.output_dir = os.path.join(args.output_dir, crud_data.tblname)
		crud_data.params.modulename = args.modulename
		dbdesc = build_dbdesc(models_dir)
		build_crud_ui(crud_data, dbdesc)

