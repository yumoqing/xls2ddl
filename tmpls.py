data_browser_tmpl = """
{
    "widgettype":"Tabular",
    "options":{
{% if title %}
		"title":"{{title}}",
{% endif %}
{% if description %}
		"description":"{{description}}",
{% endif %}
{% if not noedit %}
		"editable":{
			"new_data_url":{%- raw -%}"{{entire_url('add_{%- endraw -%}{{summary[0].name}}{%- raw -%}.dspy')}}",{%- endraw %}
			"delete_data_url":{%- raw -%}"{{entire_url('delete_{%- endraw -%}{{summary[0].name}}{%- raw -%}.dspy')}}",{%- endraw %}
			"update_data_url":{%- raw -%}"{{entire_url('update_{%- endraw -%}{{summary[0].name}}{%- raw -%}.dspy')}}"{%- endraw %}
		},
{% endif %}

        "data_url":"{%- raw -%}{{entire_url('./get_{%- endraw -%}{{summary[0].name}}{%- raw -%}.dspy')}}",{%- endraw %}
		"data_method":"{{data_method or 'GET'}}",
		"data_params":{%- raw -%}{{json.dumps(params_kw, indent=4)}},{%- endraw %}
		"row_options":{
{% if idField %}
			"idField":"{{idField}}",
{% endif %}
{% if checkField %}
			"checkField":"{{checkField}}",
{% endif %}
{% if record_toolbar %}
			"toolbar":{{json.dumps(record_toolbar, indent=4)}},
{% endif %}
{% if browserfields %}
			"browserfields": {{json.dumps(browserfields, indent=4)}},
{% endif %}
{% if editexclouded %}
			"editexclouded":{{json.dumps(editexclouded, indent=4)}},
{% endif %}
			"fields":{{json.dumps(fieldlist, indent=4)}}
        },  
{% if content_view %}
		"content_view":{{json.dumps(content_view, indent=4)}},
{% endif %}
        "page_rows":160,
        "cache_limit":5
    }
{% if binds %}
	,"binds":{{json.dumps(binds, indent=4)}}
{% endif %}
}
"""
get_data_tmpl = """
ns = params_kw.copy()
print(f'get_{{tblname}}.dspy:{ns=}')
if not ns.get('page'):
    ns['page'] = 1 
if not ns.get('sort'):
{% if sortby %}
    ns['sort'] = '{{sortby}}'
{% else %}
	ns['sort'] = 'id'
{% endif %}
filterjson = params_kw.get('data_filter')
if not filterjson:
	fields = [ f['name'] for f in {{json.dumps(fields, indent=4)}} ]
	filterjson = default_filterjson(fields, ns)
sql = '''{{sql}}'''
if filterjson:
	dbf = DBFilter(filterjson)
	conds = dbf.gen(ns)
	if conds:
		ns.update(dbf.consts)
		sql = sql.format(' and ' + conds)
else:
	sql = sql.format('')
print(f'{sql=}')
db = DBPools()
async with db.sqlorContext('{{dbname}}') as sor:
    r = await sor.sqlPaging(sql, ns) 
    return r
return {
	"total":0,
	"rows":[]
}
"""
data_new_tmpl = """
ns = params_kw.copy()
id = params_kw.id
if not id or len(id) > 32:
	id = uuid()
ns['id'] = id
db = DBPools()
async with db.sqlorContext('{{dbname}}') as sor:
    r = await sor.C('{{summary[0].name}}', ns.copy())
    return {
        "widgettype":"Message",
        "options":{
			"user_data":ns,
            "title":"Add Success",
			"timeout":3,
            "message":"ok"
        }
    }

return {
    "widgettype":"Error",
    "options":{
        "title":"Add Error",
		"timeout":3,
        "message":"failed"
    }
}
"""
data_update_tmpl = """
ns = params_kw.copy()
db = DBPools()
async with db.sqlorContext('{{dbname}}') as sor:
    r = await sor.U('{{summary[0].name}}', ns)
    print('update success');
    return {
        "widgettype":"Message",
        "options":{
            "title":"Update Success",
			"timeout":3,
            "message":"ok"
        } 
    }
        
print('update failed');
return {
    "widgettype":"Error",
    "options":{
        "title":"Update Error",
		"timeout":3,
        "message":"failed"
    }
}
"""
data_delete_tmpl = """
ns = {
    'id':params_kw['id'],
}
db = DBPools()
async with db.sqlorContext('{{dbname}}') as sor:
    r = await sor.D('{{summary[0].name}}', ns)
    print('delete success');
    return {
        "widgettype":"Message",
        "options":{
            "title":"Delete Success",
			"timeout":3,
            "message":"ok"
        }
    }

print('Delete failed');
return {
    "widgettype":"Error",
    "options":{
        "title":"Delete Error",
		"timeout":3,
        "message":"failed"
    }
}
"""
