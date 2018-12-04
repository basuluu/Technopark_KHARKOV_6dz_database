import pymysql.cursors
import time
import hashlib

class Functional():
    def __init__(self):
        with open('config.txt') as f:
            data = {}
            for line in f:
                key, value = line.split()
                data[key[:-1]] = value.strip()
        self.connection = pymysql.connect(host=data['host'], 
                                     user=data['user'], 
                                     password=data['password'], 
                                     cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.connection.cursor()
        self.sql_send('USE {};'.format(data['db_name']))

    def check_len(self, field, len_field):
        if len(field) > len_field:
            print('Your {} is too long, lenght of this field must be < {}'.format(field, len_field))
            return False
        else:
            return True
        
    def check_session(self, session):
        sql = """Select Id_user 
                 From Session
                 where Name = '{}'""".format(session)
        id_user = self.sql_send(sql)
        if len(id_user):
            id_user = id_user[0]['Id_user']
        else:
            return 0
        return id_user
    
    def check_own_blog(self, id_user, id_blog):
        if id_user:
            sql = """Select Id
                     From Blog
                     where Id_user = '{}' and Id = '{}'""".format(id_user, id_blog)
            return self.sql_send(sql)
        else:
            print('Hey dude, firstly you need to auth and only then you can do something')
        
    def sql_send(self, sql):
        self.cursor.execute(sql)
        self.connection.commit()
        result = self.cursor.fetchall()
        return result
    
    def __encrypt_pass(self, password):
        password = hashlib.md5(bytes(password, 'UTF-8')).hexdigest()
        return password
    
    def add_user(self, login, password, name, last_name):
        for field in password, name, last_name:
            if not self.check_len(field, 20):
                return
        if not self.check_len(login, 30):
            return
        password = self.__encrypt_pass(password)
        sql = """Insert 
                 Into Users (Login, Password, Name, Last_name) 
                 Values('{}', '{}', '{}', '{}');""".format(login, password, name, last_name)
        try:
            self.sql_send(sql)
        except:
            print("User with login -> '{}' already created".format(login))
            
    def auth(self, login, password):
        password = self.__encrypt_pass(password)
        sql = """Select Id 
                 From Users 
                 Where Login = '{}' and Password = '{}';""".format(login, password)
        id_user = self.sql_send(sql)
        if not len(id_user):
            print('Sorry, but User with this combination of login and password does not found')
        else:
            id_user = id_user[0]['Id']
            time_auth = time.time()
            sql = """Replace
                     Into Session (Id_user, Name)
                     Values({}, '{}');""".format(id_user, hash(login + str(time_auth)))
            self.sql_send(sql)
            return hash(login + str(time_auth))
    
    def get_users(self):
        sql = """Select Id, Login, Name, Last_name
                 From Users;
                 """
        answer = self.sql_send(sql)
        return answer
    
    def add_blog(self, name, description, session):
        id_user = self.check_session(session)
        if id_user:
            if self.check_len(name, 100):
                sql = """Insert
                         Into Blog (Name, Description, Id_user)
                         Values('{}', '{}', '{}');""".format(name, description, id_user)
                self.sql_send(sql)
        else:
            print('Hey dude, firstly you need to auth and only then you can do something')
        return
    
    def edit_blog(self, blog_id, session, name=None, description=None):
        user_id = self.check_session(session)
        if self.check_own_blog(user_id, blog_id):
            if name and self.check_len(name, 20):
                sql = """Update Blog
                         Set Name = '{}'
                         where Id = '{}';""".format(name, blog_id)
                self.sql_send(sql)
            if description:
                sql = """Update Blog
                         Set Description = '{}'
                         where Id = '{}';""".format(description, blog_id)
                self.sql_send(sql)
    
    def delete_blog(self, blog_id, session, ever=True):
        user_id = self.check_session(session)
        if self.check_own_blog(user_id, blog_id):
            if ever:
                sql = """Delete
                         From Blog
                         where Id = {};""".format(blog_id)
            else:
                sql = """Update Blog
                         Set Vision = False
                         where Id = {};""".format(blog_id)
            self.sql_send(sql)
    
    def get_blogs(self):
        sql = """Select *
                 From Blog
                 Where Vision = True;"""
        return self.sql_send(sql)
    
    def get_blogs_auth(self, session):
        user_id = self.check_session(session)
        if user_id:
            sql = """Select *
                     From Blog
                     Where Vision = True and Id_user = {};""".format(user_id)
            return self.sql_send(sql)
    
    def add_post(self, name, text, blogs, session):
        user_id = self.check_session(session)
        if user_id:
            if self.check_len(name, 100):
                sql = """Insert 
                         Into Post (Id_user, Name, Text)
                         Values('{}', '{}', '{}')""".format(user_id, name, text)
                self.sql_send(sql)
                sql = """Select Id
                         From Post
                         Order By Id Desc Limit 1;"""
                ans = self.sql_send(sql)
                ans = ans[0]['Id']
                for blog_id in blogs:
                    self.check_own_blog(user_id, blog_id)
                    if self.check_own_blog(user_id, blog_id):
                        sql = """Insert 
                                 Into Blog_Post (Id_blog, Id_post)
                                 Values('{}', '{}');""".format(blog_id, ans)
                        self.sql_send(sql)
                    else:
                        print("Sorry, you can't add post to this blog, cause u don't have enough rights")
                        
    def check_own_post(self, post_id, user_id):
        sql = """Select Id
                 From Post
                 Where Id = '{}' and Id_user = '{}';""".format(post_id, user_id)
        ans = self.sql_send(sql)
        if len(ans):
            return True
        else:
            print('Sorry, but it is not your Post')
            return False
    
    def edit_post(self, post_id, session, name=None, text=None, blogs=None):
        user_id = self.check_session(session)
        if user_id and self.check_own_post(post_id, user_id):
            if name:
                sql = """Update Post
                         Set Name = '{}'
                         where Id = '{}' and Id_user = '{}';""".format(name, post_id, user_id)
                self.sql_send(sql)
            if text:
                sql = """Update Post
                         Set Text = '{}'
                         Where Id = '{}' and Id_user = '{}';""".format(text, post_id, user_id)
                self.sql_send(sql)
            if blogs:
                sql = """Select Id_blog
                         From Blog_Post
                         Where Id_post = '{}';""".format(post_id)
                ans = self.sql_send(sql)
                current_blogs = []
                for blog in ans:
                    current_blogs.append(blog['Id_blog'])
                for blog_id in blogs:
                    if blog_id not in current_blogs and len(self.check_own_blog(user_id, blog_id)):
                        sql = """Insert 
                                 Into Blog_Post (Id_blog, Id_post)
                                 Values('{}', '{}');""".format(blog_id, post_id)
                        self.sql_send(sql)
                for blog_id in current_blogs:
                    if blog_id not in blogs:
                        sql = """Delete
                                 From Blog_Post
                                 Where Id_blog = '{}' and Id_post = '{}'""".format(blog_id, post_id)
                        self.sql_send(sql)
                    
                    else:
                        print("Sorry, you can't add post to this blog, cause u don't have enough rights")
                
    def delete_post(self, post_id, session):
        user_id = self.check_session(session)
        if user_id and self.check_own_post(post_id, user_id):
            sql = """Delete
                     From Post
                     Where Id = '{}' and Id_user = '{}'""".format(post_id, user_id)
            self.sql_send(sql)
            
    def add_comment(self, post_id, text, session, comment_id=0):
        user_id = self.check_session(session)
        if user_id:
            sql = """Insert 
                     Into Comment (Id_post, Id_user, Id_comment, Text)
                     Values('{}', '{}', '{}', '{}')""".format(post_id, user_id, comment_id, text)
            self.sql_send(sql)
    
    def get_user_comment(self, post_id, user_id):
        sql = """Select Text
                 From Comment
                 Where Id_post = '{}' and Id_user = '{}'""".format(post_id, user_id)
        return self.sql_send(sql)
    
    def get_branch_comment(self, comment_id):
        text = []
        comments_id = [comment_id]
        sql = """Select Text
                 From Comment
                 Where Id = '{}'""".format(comment_id)
        ans = self.sql_send(sql)
        if len(ans):
            text.append(ans[0]['Text'])
        while(len(comments_id)):
            comment_id = comments_id.pop()
            sql = """Select Id, Text
                     From Comment
                     Where Id_comment = '{}'""".format(comment_id)
            ans = self.sql_send(sql)
            if len(ans):
                for res in ans:
                    text.append(res['Text'])
                    comments_id.append(res['Id'])
        return text
    
    def get_comment_history(self, users, blog_id):
        if isinstance(users, list):
            users = tuple(users)
        sql = """Select Id_user, Text 
                 From Comment 
                 Where Id_user in {} and 
                 Id_post in (Select Id_Post 
                             From Blog_Post 
                             Where Id_Blog={});""".format(users, blog_id)
        ans = self.sql_send(sql)
        comments = {}
        for res in ans:
            user_id = res['Id_user']
            if user_id not in comments.keys():
                comments[user_id] = []
            else:
                comments[user_id].append(res['Text'])
        return comments
