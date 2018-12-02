import pymysql.cursors

class INDEX():
    def __init__(self):
        with open('config.txt') as f:
            data = {}
            for line in f:
                key, value = line.split()
                data[key[:-1]] = value.strip()
        connection = pymysql.connect(host=data['host'], 
                                     user=data['user'], 
                                     password=data['password'], 
                                     cursorclass=pymysql.cursors.DictCursor)
        self.cursor = connection.cursor()
        self.sql_send('USE {};'.format(data['db_name']))
        self.create_index()
        self.cursor.close()
        connection.close()

    def sql_send(self, sql):
        self.cursor.execute(sql)

    def create_index(self):
        sql = ["CREATE INDEX post_user ON Comment(Id_post, Id_user);",
               "CREATE INDEX log ON Users(Login);",
               "CREATE INDEX blog_post ON Blog_Post(Id_blog, Id_post);"]
        for message in sql:
            self.sql_send(message)

h = INDEX()
