data_browser_tmpl = """
{
    "widgettype":"Tabular",
    "options":{
		"title":"{{tblname}}",
		"editable":{
			"new_data_url":{%- raw -%}"{{entire_url('add_{%- endraw -%}{{summary[0].name}}{%- raw -%}.dspy')}}",{%- endraw %}
			"delete_data_url":{%- raw -%}"{{entire_url('delete_{%- endraw -%}{{summary[0].name}}{%- raw -%}.dspy')}}",{%- endraw %}
			"update_data_url":{%- raw -%}"{{entire_url('update_{%- endraw -%}{{summary[0].name}}{%- raw -%}.dspy')}}"{%- endraw %}
		},

        "data_url":"{%- raw -%}{{entire_url('./get_{%- endraw -%}{{summary[0].name}}{%- raw -%}.dspy')}}",{%- endraw %}
        "record_view":{
            "widgettype":"DataRow",
            "options":{
                "fields":{{fieldlist}}
            },  
        },  
        "page_rows":800,
        "cache_limit":5
    }   
}
"""
get_data_tmpl = """
ns = params_kw.copy()
if not ns.get('page'):
    ns['page'] = 1 
if not ns.get('sort'):
    ns['sort'] = 'name'
if ns.get('name'):
    ns['name'] = '%' + params_kw['name'] + '%' 

db = DBPools()
async with db.sqlorContext('{{dbname}}') as sor:
    sql = '''{{sql}}'''
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
