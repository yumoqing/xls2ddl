# xls2ddl

a tool to create related database schema from xlsx file

there is a xlsx template file called "model.xlst" in this repo

## How to use it

1 double click "model.xlst"
2 in "sammary" datasheet, wirte the table name, table label, primary key
3 in "fields" datasheet, create all the field in the table
4 in "validation" datashhet identifies the index
  first column is index name
  second column choose the "idx"
  thrid column for duplicatable index use "index:f1,f2 ..." or "unique:f1, f2, ..." for unique index

5 save it with the tablenme as xlsx file's name
6 repeat 1 to 5 for all the table.
7 translates all xlsx file to ddl sql using
in the folder hold all the xlsx file

for mysql
```
python path/to/xls2ddl.py mysql .
```
for sqlite3
```
python path/to/xls2ddl.py sqlite3 .
```
for oracle
```
python path/to/xls2ddl.py oracle .
```
for postgresql
```
python path/to/xls2ddl.py postgresql .
```
for sqlserver
```
python path/to/xls2ddl.py sqlserver .
```
## examples xlsx file
open the [examples.xlsx](./examples.xlsx) to find out how to write a table schema infomation

write your table schema info file:

1 copy examples.xlsx file to 'your table name'.xlsx
2 open 'your table name'.xlsx and change information in summary, fields, validation codes
3 save it
4 use xls2ddl translates xlsx file to ddl file
5 use the ddl file to create you database tables

# xls2crud
xls2crud is a tool to create table data administration website user interface.
it is only support [ahserver](https://git.kaiyuancloud.cn/yumoqing/ahserver) backend server and [bricks](https://git.kaiyuancloud.cn/yumoqing/bricks) front end




