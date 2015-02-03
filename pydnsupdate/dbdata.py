__author__ = 'tlo'

import mysql.connector
from mysql.connector import errorcode
from mysql.connector import connect


class DbData(object):
    def __init__(self):

        try:
            self.db = connect(option_files='/home/tlo/.my.cnf')

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Bad password or Username")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Non existent database")
            else:
                print(err)

        self.cursorquery = self.db.cursor(buffered=True)
        self.cursorinput = self.db.cursor(buffered=True)

        self.insert_new_ip = (
            "INSERT INTO addresses (routerid, address) "
            "VALUES (%s, %s)"
        )

    def getcurrent(self):
        self.cursorquery.execute("SELECT * FROM lastaddress")
        return self.cursorquery

    def savenew(self, routerid, routeraddress):
        self.cursorinput.execute(self.insert_new_ip, (routerid, routeraddress))
        self.db.commit()

    def close(self):
        self.cursorquery.close()
        self.cursorinput.close()
        self.db.close()