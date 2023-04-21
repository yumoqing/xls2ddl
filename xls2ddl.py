# -*- coding:utf-8 -*-
import io
import sys
from traceback import print_exc
from xlsxData import CRUDData, xlsxFactory

import codecs
import json
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
	if xlsfile.endswith('json'):
		with codecs.open(xlsfile,'r','utf-8') as f:
			data = json.load(f)
	else:
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
	for f in listFile(folder, suffixs=['xlsx','json']):
		try:
			s = xls2ddl(f,dbtype)
			ddl_str='%s%s' % (ddl_str, s)
		except Exception as e:
			print('Exception:',e,'f=',f)
			print_exc()
	return ddl_str

if __name__ == '__main__':
	import sys
	##解决windows 终端中输出中文出现 
	# UnicodeEncodeError: 'gbk' codec can't encode character '\xa0' in position 20249
	# 错误
	# BEGIN
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
	#
	# END
	if len(sys.argv) < 3:
		print('Usage:%s dbtype folder' % sys.argv[0])
		sys.exit(1)

	s = model2ddl(sys.argv[2], sys.argv[1])
	print(s)

