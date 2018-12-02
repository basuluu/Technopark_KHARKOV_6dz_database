import pymysql.cursors

class MAKE_DB():
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
        self.run(data['db_name'])
        self.cursor.close()
        connection.close()
        
    def sql_send(self, sql):
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result
        
    def build_db(self, name):
        self.sql_send('Drop database if Exists {};'.format(name))
        self.sql_send('Create database {};'.format(name))
        
    def build_tables(self):
        self.create_users()
        self.create_session()
        self.create_blog()
        self.create_post()
        self.create_blog_post()
        self.create_comment()
        self.create_index()
        
    def create_users(self):
        sql = """CREATE TABLE Users
                (
                    Id INT AUTO_INCREMENT,
                    Login VARCHAR(30) UNIQUE,
                    Password VARCHAR(32) NOT NULL,
                    Name VARCHAR(20) NOT NULL,
                    Last_name VARCHAR(20) NOT NULL,
                    Primary key(Id),
                    Unique key(Login)
                );"""
        self.sql_send(sql)
    
    def create_session(self):
        sql = """CREATE TABLE Session
                (
                    Id_session INT AUTO_INCREMENT,
                    Id_user INT UNIQUE,
                    Name VARCHAR(100),
                    Primary key(Name),
                    Unique key(Id_session),
                    Foreign key(Id_user) references Users(Id)
                );"""
        self.sql_send(sql)
        
    def create_blog(self):
        sql = """CREATE TABLE Blog
                (
                    Id INT AUTO_INCREMENT,
                    Id_user INT,
                    Name VARCHAR(100),
                    Description TEXT,
                    Vision BOOLEAN DEFAULT True,
                    Primary key(Id),
                    Foreign key(Id_user) references Users(Id)
                );"""
        self.sql_send(sql)
        
    def create_post(self):
        sql = """CREATE TABLE Post
                (
                    Id INT AUTO_INCREMENT,
                    Id_user INT,
                    Name VARCHAR(100),
                    Text TEXT,
                    Primary key(Id),
                    Foreign key(Id_user) references Users(Id)
                );"""
        self.sql_send(sql)
    
    def create_blog_post(self):
        sql = """CREATE TABLE Blog_Post
                (
                    Id_blog INT,
                    Id_post INT,
                    Foreign key(Id_blog) references Blog(Id) on delete cascade,
                    Foreign key(Id_post) references Post(Id) on delete cascade
                );"""
        self.sql_send(sql)
        
    def create_comment(self):
        sql = """CREATE TABLE Comment
                (
                    Id INT AUTO_INCREMENT,
                    Id_post INT,
                    Id_user INT,
                    Id_comment INT DEFAULT 0,
                    Text TEXT,
                    Primary key(Id),
                    Foreign key(ID_post) references Post(Id) on delete cascade,
                    Foreign key(Id_user) references Users(Id)
                );"""
        self.sql_send(sql)
        
    def create_index(self):
        sql = ["CREATE INDEX post_user ON Comment(Id_post, Id_user);",
               "CREATE INDEX log ON Users(Login);",
               "CREATE INDEX blog_post ON Blog_Post(Id_blog, Id_post);"]
        for message in sql:
            self.sql_send(message)
        
        
    def run(self, db_name):
        self.build_db(db_name)
        self.sql_send('USE {};'.format(db_name))
        self.build_tables()
        
h = MAKE_DB()

