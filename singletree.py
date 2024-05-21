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
{% if editable %}
		"editable":{
			"fields":{{json.dumps(edit_fields)}},
			"add_url":{%- raw -%}"{{entire_url('./new_{%- endraw -%}{{table}}{%- raw -%}.dspy')}}",{%- endraw %}
			"update_url":{%- raw -%}"{{entire_url('./update_{%- endraw -%}{{table}}{%- raw -%}.dspy')}}",{%- endraw %}
			"delete_url":{%- raw -%}"{{entire_url('./delete_{%- endraw -%}{{table}}{%- raw -%}.dspy')}}"{%- endraw %}
		},
{% endif %}
{% if checkable %}
		"checkable":true,
{% endif %}
		"parentField":"{{parentField}}",
		"idField":"{{idField}}",
		"textField":"{{textField}}",
		"dataurl":{%- raw -%}"{{entire_url('./get_{%- endraw -%}{{table}}{%- raw -%}.dspy')}}",{%- endraw %}
	}
{% if binds %}
	,"binds":{{json.dumps(binds)}}
{% endif %}
}
"""
get_nodes_tmpl = """
ns = params_kw.copy()
sql = '''select * from {{table}} where 1 = 1'''
id = ns.get('{{idField}}')
if id:
	sql += " and {{parentField}} = ${id}$"
else:
	sql += " and {{parentField}} is null"

db = DBPools()
async with db.sqlorContext('{{dbname}}') as sor:
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
	with open(os.path.join(pat, f'delete_{d.table}.dspy'), 'w') as f:
		f.write(s)

def gen_update_nodedata(d, pat):
	e = MyTemplateEngine([])
	s = e.renders(data_update_tmpl, d)
	with open(os.path.join(pat, f'update_{d.table}.dspy'), 'w') as f:
		f.write(s)

def gen_new_nodedata(d, pat):
	e = MyTemplateEngine([])
	s = e.renders(data_new_tmpl, d)
	with open(os.path.join(pat, f'new_{d.table}.dspy'), 'w') as f:
		f.write(s)

def gen_get_nodedata(d, pat):
	e = MyTemplateEngine([])
	s = e.renders(get_nodes_tmpl, d)
	with open(os.path.join(pat, f'get_{d.table}.dspy'), 'w') as f:
		f.write(s)

def gen(dbdesc, txt, outdir):
	d = DictObject(json.loads(txt))
	tbldesc = dbdesc[d.table]
	exclouds = d.edit_exclouded_fields or []
	if d.idField not in exclouds:
		exclouds.append(d.idField)
	if d.parentField not in exclouds:
		exclouds.append(d.parentField)
	print(f'{exclouds=}')
	d.edit_fields = [ f for f in field_list(dbdesc[d.table]) if f.name not in exclouds ]
	
	outdir = os.path.join(outdir, d.table)
	_mkdir(outdir)
	d.update(tbldesc)
	gen_tree_ui(d, outdir)
	gen_get_nodedata(d, outdir)
	gen_new_nodedata(d, outdir)
	gen_update_nodedata(d, outdir)
	gen_delete_nodedata(d, outdir)

def main(dbdesc, fn, outdir):
	with codecs.open(fn, 'r', 'utf-8') as f:
		gen(dbdesc, f.read(), outdir)

if __name__ == '__main__':
	if len(sys.argv) < 4:
		print(f'{sys.argv[0]} model_path outpath tree_desc_file ...')
		sys.exit(1)
	dbdesc = build_dbdesc(sys.argv[1])
	outdir = sys.argv[2]
	for f in sys.argv[3:]:
		main(dbdesc, f, outdir)

