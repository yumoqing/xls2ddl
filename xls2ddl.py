from xlsxData import CRUDData, xlsxFactory

from sqlor.ddl_template_sqlserver import sqlserver_ddl_tmpl
from sqlor.ddl_template_mysql import mysql_ddl_tmpl
from sqlor.ddl_template_oracle import oracle_ddl_tmpl
from sqlor.ddl_template_postgresql import postgresql_ddl_tmpl

from appPublic.myTE import MyTemplateEngine
from appPublic.folderUtils import listFile

tmpls = {
	"sqlserver":sqlserver_ddl_tmpl,
	"mysql":mysql_ddl_tmpl,
	"oracle":oracle_ddl_tmpl,
	"postgresql":postgresql_ddl_tmpl
}

def xls2ddl(xlsfile,dbtype):
	d = xlsxFactory(xlsfile)
	data = d.read()
	tmpl = tmpls.get(dbtype.lower())
	if tmpl is None:
		raise Exception('%s database not implemented' % dbtype)
	e = MyTemplateEngine([])
	s = e.renders(tmpl,data)
	return s

def model2ddl(folder,dbtype):
	ddl_str = ''
	for f in listFile(folder, suffixs=['xlsx']):
		try:
			s = xls2ddl(f,dbtype)
			ddl_str='%s%s' % (ddl_str, s)
		except:
			pass
	return ddl_str

if __name__ == '__main__':
	import sys
	if len(sys.argv) < 3:
		print('Usage:%s dbtype folder' % sys.argv[0])
		sys.exit(1)

	s = model2ddl(sys.argv[2], sys.argv[1])
	print(s)

