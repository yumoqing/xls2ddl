data_browser_tmpl = """
{
    "widgettype":"Tabular",
    "options":{
{% if title %}
		"title":"{{tblname}}",
{% endif %}
{% if description %}
		"description":"{{description}}",
{% endif %}
		"editable":{
			"new_data_url":{%- raw -%}"{{entire_url('add_{%- endraw -%}{{summary[0].name}}{%- raw -%}.dspy')}}",{%- endraw %}
			"delete_data_url":{%- raw -%}"{{entire_url('delete_{%- endraw -%}{{summary[0].name}}{%- raw -%}.dspy')}}",{%- endraw %}
			"update_data_url":{%- raw -%}"{{entire_url('update_{%- endraw -%}{{summary[0].name}}{%- raw -%}.dspy')}}"{%- endraw %}
		},

        "data_url":"{%- raw -%}{{entire_url('./get_{%- endraw -%}{{summary[0].name}}{%- raw -%}.dspy')}}",{%- endraw %}
		"data_method":"{{data_method or 'GET'}}",
		"data_params":{%- raw -%}{{json.dumps(params_kw)}},{%- endraw %}
		"row_options":{
{% if record_toolbar %}
			"toolbar":{{json.dumps(record_toolbar)}},
{% endif %}
{% if browserfields %}
			"browserfields":{{json.dumps(browserfields)}},
{% endif %}
{% if editexclouded %}
			"editexclouded":{{json.dumps(editexclouded)}},
{% endif %}
			"fields":{{json.dumps(fieldlist)}}
        },  
{% if content_view %}
		"content_view":{{json.dumps(content_view)}},
{% endif %}
        "page_rows":160,
        "cache_limit":5
    }   
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
	fields = [ f['name'] for f in {{json.dumps(fields)}} ]
	filterjson = default_filterjson(fields, ns)
sql = '''{{sql}}'''
if filterjson:
	dbf = DBFilter(filterjson)
	conds = dbf.gen(ns)
	ns.update(dbf.consts)
	sql += ' and ' + conds

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
id = uuid()
ns['id'] = id
db = DBPools()
async with db.sqlorContext('{{dbname}}') as sor:
    r = await sor.C('{{summary[0].name}}', ns)
    return {
        "widgettype":"Message",
        "options":{
            "title":"Add Success",
            "message":"ok"
        }
    }

return {
    "widgettype":"Error",
    "options":{
        "title":"Add Error",
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
            "message":"ok"
        } 
    }
        
print('update failed');
return {
    "widgettype":"Error",
    "options":{
        "title":"Update Error",
        "message":"failed"
    }
}
"""
data_delete_tmpl = """
ns = {
    'id':params_kw['id'],
    'del_flg':'1'
}
db = DBPools()
async with db.sqlorContext('{{dbname}}') as sor:
    r = await sor.D('{{summary[0].name}}', ns)
    print('delete success');
    return {
        "widgettype":"Message",
        "options":{
            "title":"Delete Success",
            "message":"ok"
        }
    }

print('Delete failed');
return {
    "widgettype":"Error",
    "options":{
        "title":"Delete Error",
        "message":"failed"
    }
}
"""
