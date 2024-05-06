data_browser_tmpl = """
{
    "widgettype":"Tabular",
    "options":{
		"title":"{{tblname}}",
		"editable":{
			"form_cheight":4,
			"new_data_url":{%- raw -%}"{{entire_url('add_{%- endraw -%}{{tblname}}{%- raw -%}.dspy')}}",{%- endraw -%}
			"delete_data_url":{%- raw -%}"{{entire_url('delete_{%- endraw -%}{{tblname}}{%- raw -%}.dspy')}}",{%- endraw -%}
			"update_data_url":{%- raw -%}"{{entire_url('update_{%- endraw -%}{{tblname}}{%- raw -%}.dspy')}}"{%- endraw -%}
		},

        "data_url":"{%- raw -%}{{entire_url('./get_{%- endraw -%}{{summary[0].name}}{%- raw -%}.dspy')}}",{%- endraw -%}
        "record_view":{
            "widgettype":"DataRow",
            "options":{
                "fields":{{fields}},
                "height":"100%"
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
}
"""
data_new_tmpl = """
ns = params_kw.copy()
id = uuid()
ns['id'] = id
db = DBPools()
async with db.sqlorContext('{{dbname}}') as sor:
    r = await sor.C('{{tblname}}', ns)
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
    r = await sor.U('{{tblname}}', ns)
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
    r = await sor.U('{{tblname}}', ns)
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
