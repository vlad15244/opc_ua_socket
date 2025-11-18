import mysql.connector
import abc

ConnectionString = {
    'host' : 'localhost',
    'user' : 'root',
    'password' : '1234',
    'database' : 'robot_line'        
}

SqlField = {
    'ID' : 'INT AUTO_INCREMENT PRIMARY KEY',
    'NAME' : 'VARCHAR(25) NOT NULL',
    'NAME_1' : 'VARCHAR(25) NOT NULL',   
    'TimestampAdd' : 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
}

class Database:
    cnx = None
    table_name = None
    sql_field = None
    def __init__(self, connection, field, table_name):

        self.sql_field = field
        self.table_name = table_name
        self.cnx = mysql.connector.connect(
            host=connection['host'],
            user=connection['user'],
            password=connection['password'],
            database=connection['database']
        ) 

    def create_table(self):

        query = 'CREATE TABLE IF NOT EXISTS '
        query += self.table_name
        query += ' ('
        query += ', '.join(f"{key} {value}" for key, value in self.sql_field.items())
        query += ') '
        

        if self.cnx.is_connected:
            self.cnx.cursor().execute(query)
        else:
            print("База данных не подключена")

    def get_all(self, **kwargs):
        query = 'SELECT * FROM '
        query += self.table_name

        if len(kwargs) != 0:
            query += " WHERE "
            query +=  ' AND '.join(f"{key} = '{value}'" for key, value in kwargs.items()) 

        if self.cnx.is_connected:
            cursor = self.cnx.cursor()
            cursor.execute(query)

            if len(cursor.fetchall()) == 0:
                print("Результат ответа пустой")
            else:                
                return cursor.fetchall()
        else:
            print("База данных не подключена") 

    def order_by(self, *args, DESC : bool):
        query = 'SELECT * FROM '
        query += self.table_name
        query += ' ORDER BY '

        if len(args) == 0:
            pass
        else:
            for arg in args:
                  query += arg
                  query += ','                      
    
        query = query[:-1]
        if DESC:
            query += ' DESC '
        else:
            query += ' ASC '            

        if self.cnx.is_connected:
            cursor = self.cnx.cursor()
            cursor.execute(query)

            if len(cursor.fetchall()) == 0:
                print("Результат ответа пустой")
            else:    
                result = cursor.fetchall()  

                for d in result:
                    print(d)         
                return result
        else:
            print("База данных не подключена")     


    def insert(self, *args):
        query = 'INSERT INTO '
        query += self.table_name
        query += "("       
        query += ','.join(f" {key} " for key, value in self.sql_field.items() if 'PRIMARY KEY' not in value and 'CURRENT_TIMESTAMP' not in value )
        query += ")"          
        query += " VALUES ("

        if len(args) == 0:
            pass
        else:
            params = ''
            for arg in args:
                params += "%s,"
        params = params[:-1]   
        query += params
        query += ")"   
        if self.cnx.is_connected:
            pass
            cursor = self.cnx.cursor()
            cursor.execute(query,args)

            self.cnx.commit()
        else:
            print("База данных не подключена")

    def insert_many(self, obj_data):
        query = 'INSERT INTO '
        query += self.table_name
        query += "("       
        query += ','.join(f" {key} " for key, value in self.sql_field.items() if 'PRIMARY KEY' not in value and 'CURRENT_TIMESTAMP' not in value )
        query += ")"          
        query += " VALUES ("

        if len(obj_data) == 0:
            pass
        else:
            params = ''
            for arg in obj_data[1]:
                params += "%s,"
        params = params[:-1]   
        query += params
        query += ")"   

        if self.cnx.is_connected:
            pass
            cursor = self.cnx.cursor()
            cursor.executemany(query,obj_data)

            self.cnx.commit()
        else:
            print("База данных не подключена")        

      
db = Database(ConnectionString,SqlField,'example2')
db.create_table()
"""value = [('vlad', 'test'), ('vlad1', 'test1'), ('vlad3', 'test3')]
db.insert_many(value)"""
sql_response = db.get_all()
