#! /usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, ast, MySQLdb
parser = argparse.ArgumentParser()
parser.add_argument('input', help='The file with database definitions, tables and fields to add the 9th digit')
args = parser.parse_args()
mobile_prefix = ['0', '1', '6', '7', '8', '9']
operations = 0

print 'Trying to open the file in {}'.format(args.input)
database_defitions = open(args.input, 'rb')
if database_defitions:
    definitions = ast.literal_eval(database_defitions.read())
    database_defitions.close()
    db = MySQLdb.connect(host=definitions['host'], user=definitions['username'], passwd=definitions['password'], db=definitions['database'])
    if db:
        cursor = db.cursor()
        for table in definitions['tables']:
            print 'Getting values from table {}'.format(table)
            for field in definitions['tables'][table]:
                print 'Getting values from field {}'.format(field)
                query = 'SELECT id,{} FROM {} WHERE {} LIKE \'(11)%\''.format(field, table, field)
                cursor.execute(query)
                results = cursor.fetchall()
                for result in results:
                    if len(result[1]) < 15:
                        splited = result[1].split()
                        query = None
                        if len(splited) > 1:
                            if splited[1][0] in mobile_prefix:
                                query = 'UPDATE {} SET {}={} WHERE id = {}'.format(table, field, '\'' + splited[0] + ' 9' + splited[1] + '\'', result[0])
                        else:
                            if splited[0][4:][0] in mobile_prefix:
                                query = 'UPDATE {} SET {}={} WHERE id = {}'.format(table, field, '\'' + splited[0][0:4] + ' 9' + splited[0][4:] + '\'', result[0])

                        if query:
                            cursor.execute(query);
                            db.commit()
                            operations += cursor.rowcount
        cursor.close()
        db.close()
        print '{} mobile phones are now migrated with the 9th digit'.format(operations)
    else:
        print 'Can\'t connect to the database stored in the input file'
else:
    print 'Can\'t open the file {}'.format(args.input)