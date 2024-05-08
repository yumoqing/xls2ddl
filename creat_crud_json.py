import os
import sys
import json
import codecs
from xls2crud import build_dbdesc
from appPublic.folderUtils import _mkdir

def create_crud(modelspath:str, outpath: str, ui_path: str, dbname:str, tblname:str):
	d = {
		"models_dir":modelspath,
		"output_dir": os.path.join(ui_path, tblname),
		"dbname":dbname,
		"tblname":tblname,
		"params":{
			"browserfields":{
				"excloud":[],
				"cwidth":{}
			},
			"editexclouded":[],
			"record_toolbar":None,
			"content_view":None,
		}
	}
	fn = os.path.join(outpath, f'{tblname}.json')
	with codecs.open(fn, 'w', 'utf-8') as f:
		txt = json.dumps(d, indent=4)
		f.write(txt)

def main():
	model_path = sys.argv[1]
	ui_path = sys.argv[2]
	outpath = sys.argv[3]
	dbname = sys.argv[4]
	dbdesc = build_dbdesc(model_path)
	_mkdir(outpath)
	for tbname, desc in dbdesc.items():
		create_crud(model_path, outpath, ui_path, dbname, tbname)

if __name__ == '__main__':
	if len(sys.argv) < 5:
		print(f'{sys.argv[0]} models_path ui_path outpath dbname')
		sys.exit(1)
	
	main()
