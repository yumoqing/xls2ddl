from xls2crud import build_dbdesc, build_crud_ui
if __name__ == '__main__':
	"""
	crud_json has following format
	{
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
	dbdesc = build_dbdesc(args.models_dir)
	for fn in args.files:
		print(f'handle {fn}')
		crud_data = {}
		with codecs.open(fn, 'r', 'utf-8') as f:
			a = json.load(f)
			ac = ArgsConvert('${','}$')
			a = ac.convert(a,ns)
			crud_data = DictObject(**a)
			tblname = crud_data.alias or crud_data.tblname
			crud_data.output_dir = os.path.join(args.output_dir, tblname)
		crud_data.params.modulename = args.modulename
		if crud_data.uitype == 'tabular':
			build_crud_ui(crud_data, dbdesc)
			continue
		if crud_data.uitype == 'tree':
			build_tree_ui(crud_data, dbdesc)
			continue
