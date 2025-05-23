import os
import sys
import codecs
import json
from appPublic.dictObject import DictObject
from xlsxData import xlsxFactory
from appPublic.folderUtils import listFile, _mkdir
from appPublic.myTE import MyTemplateEngine
from tmpls import data_browser_tmpl, get_data_tmpl, data_new_tmpl, data_update_tmpl, data_delete_tmpl
from xls2crud import build_dbdesc, field_list
from tmpls import data_new_tmpl, data_update_tmpl, data_delete_tmpl

ui_tmpl = """
{
	"widgettype":"Tree",
	"options":{
{% if not notitle %}
{% if title %}
		"title":"{{title}}",
{% else %}
		"title":"{{summary[0].title}}",
{% endif %}
{% endif %}
{% if description %}
		"description":"{{description}}",
{% endif %}
{% if toolbar %}
		"toolbar":{{json.dumps(toolbar, ensure_ascii=False)}},
{% endif %}
{% if editable %}
		"editable":{
			"fields":{{edit_fields_str}},
			"add_url":{%- raw -%}"{{entire_url('./new_{%- endraw -%}{{tblname}}{%- raw -%}.dspy')}}",{%- endraw %}
			"update_url":{%- raw -%}"{{entire_url('./update_{%- endraw -%}{{tblname}}{%- raw -%}.dspy')}}",{%- endraw %}
			"delete_url":{%- raw -%}"{{entire_url('./delete_{%- endraw -%}{{tblname}}{%- raw -%}.dspy')}}"{%- endraw %}
		},
{% endif %}
{% if checkField %}
		"checkField":"{{checkField}}",
{% endif %}
		"parentField":"{{parentField}}",
		"idField":"{{idField}}",
		"textField":"{{textField}}",
		"dataurl":{%- raw -%}"{{entire_url('./get_{%- endraw -%}{{tblname}}{%- raw -%}.dspy')}}"{%- endraw %}
	}
{% if binds %}
	,"binds":{{json.dumps(binds, indent=4, ensure_ascii=False)}}
{% endif %}
}
"""
get_nodes_tmpl = """
ns = params_kw.copy()
sql = '''select * from {{tblname}} where 1 = 1'''
id = ns.get('{{idField}}')
if id:
	sql += " and {{parentField}} = ${id}$"
else:
	sql += " and {{parentField}} is null"

sql += " order by {{textField}} "
db = DBPools()
dbname = get_module_dbname('{{modulename or ''}}')
async with db.sqlorContext(dbname) as sor:
	r = await sor.sqlExe(sql, ns)
	return r
return []
"""

def gen_tree_ui(d, pat):
	e = MyTemplateEngine([])
	s = e.renders(ui_tmpl, d)
	with open(os.path.join(pat, f'index.ui'), 'w') as f:
		f.write(s)
	
def gen_delete_nodedata(d, pat):
	e = MyTemplateEngine([])
	s = e.renders(data_delete_tmpl, d)
	with open(os.path.join(pat, f'delete_{d.tblname}.dspy'), 'w') as f:
		f.write(s)

def gen_update_nodedata(d, pat):
	e = MyTemplateEngine([])
	s = e.renders(data_update_tmpl, d)
	with open(os.path.join(pat, f'update_{d.tblname}.dspy'), 'w') as f:
		f.write(s)

def gen_new_nodedata(d, pat):
	e = MyTemplateEngine([])
	s = e.renders(data_new_tmpl, d)
	with open(os.path.join(pat, f'new_{d.tblname}.dspy'), 'w') as f:
		f.write(s)

def gen_get_nodedata(d, pat):
	e = MyTemplateEngine([])
	s = e.renders(get_nodes_tmpl, d)
	with open(os.path.join(pat, f'get_{d.tblname}.dspy'), 'w') as f:
		f.write(s)

def build_tree_ui(tree_data, dbdesc):
	outdir = tree_data.output_dir
	_mkdir(outdir)
	tbldesc = dbdesc[tree_data.tblname].copy()
	tbldesc = DictObject(**tbldesc)
	tbldesc.tblname = tree_data.tblname
	tbldesc.update(tree_data.params)
	exclouds = tbldesc.edit_exclouded_fields or []
	if tbldesc.idField not in exclouds:
		exclouds.append(tbldesc.idField)
	if tbldesc.parentField not in exclouds:
		exclouds.append(tbldesc.parentField)
	tbldesc.edit_fields_str = json.dumps([ f for f in field_list(tbldesc) if f.name not in exclouds ],
							indent=4, ensure_ascii=False)
	gen_tree_ui(tbldesc, outdir)
	gen_get_nodedata(tbldesc, outdir)
	gen_new_nodedata(tbldesc, outdir)
	gen_update_nodedata(tbldesc, outdir)
	gen_delete_nodedata(tbldesc, outdir)

def main(dbdesc, outdir, modulename, fn):
	with codecs.open(fn, 'r', 'utf-8') as f:
		gen(dbdesc, outdir, modulename, f.read())
	
def main(dbdesc, outdir, modulename, fn):
	with codecs.open(fn, 'r', 'utf-8') as f:
		gen(dbdesc, outdir, modulename, f.read())

if __name__ == '__main__':
	if len(sys.argv) < 4:
		print(f'{sys.argv[0]} model_path outpath modelname tree_desc_file ...')
		sys.exit(1)
	dbdesc = build_dbdesc(sys.argv[1])
	outdir = sys.argv[2]
	modulename = sys.argv[3]
	for f in sys.argv[4:]:
		main(dbdesc, outdir, modulename, f)

