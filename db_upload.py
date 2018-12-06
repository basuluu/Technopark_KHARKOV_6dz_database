%%time
import collections
import faker
import Functional
import random

class db_upload():
    def __init__(self, users=1000, blogs=100, posts=10000, comments=100000):
        self.users = users
        self.blogs = blogs
        self.posts = posts
        self.comments = comments
        self.users_login = set()
        self.user_blog = {}
        self.fake = faker.Faker()
        self.db = Functional.Functional()
        self.run()
    
    def gen_login(self):
        login = self.fake.email()
        if len(login) > 30 or login in self.users_login:
            login = self.gen_login()
        self.users_login.add(login)
        return login
    
    def upload_users(self):
        users_ins = []
        for _ in range(self.users):
            login = self.gen_login()
            password = self.fake.password(8)
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            users_ins.append("('{}', '{}', '{}', '{}')".format(login, password, first_name, last_name))
        sql = """Insert
                 Into Users (Login, Password, Name, Last_name) 
                 Values"""
        users_ins = ', '.join(users_ins)
        sql = ' '.join((sql, users_ins)) + ';'
        self.db.sql_send(sql)
        self.users_login.clear()
    
    def upload_blogs(self):
        blogs_ins = []
        for _ in range(self.blogs):
            user_id = random.randint(1, self.users)
            name_blog = self.fake.company()
            if user_id not in self.user_blog.keys():
                self.user_blog[user_id] = [_+1]
            else:
                self.user_blog[user_id].append(_+1)
            description = ''.join(self.fake.paragraph(2))
            blogs_ins.append("('{}', '{}', '{}')".format(user_id, name_blog, description))
        sql = """Insert
                 Into Blog (Id_user, Name, Description)
                 Values"""
        blogs_ins = ', '.join(blogs_ins)
        sql = ' '.join((sql, blogs_ins)) + ';'
        self.db.sql_send(sql)
            
    def upload_posts(self):
        users_id = list(self.user_blog.keys())
        post_ins = []
        blog_post_ins = []
        for _ in range(self.posts):
            user_id = random.choice(users_id)
            if len(self.user_blog[user_id]) > 1:
                blog_id = random.choice(self.user_blog[user_id])
            else:
                blog_id = self.user_blog[user_id][0]
            name_post = self.fake.sentence(random.randint(1,6))
            text_post = self.fake.text(random.randint(100, 600))
            post_ins.append("('{}', '{}', '{}')".format(user_id, name_post, text_post))
            blog_post_ins.append("('{}', '{}')".format(blog_id, _+1))
        post_ins = ', '.join(post_ins)
        blog_post_ins = ', '.join(blog_post_ins)
        sql = """Insert
                 Into Post (Id_user, Name, Text)
                 Values"""
        sql = ' '.join((sql, post_ins)) + ';'
        self.db.sql_send(sql)
        sql = """Insert
                 Into Blog_Post (Id_blog, Id_post)
                 Values"""
        sql = ' '.join((sql, blog_post_ins)) + ';'
        self.db.sql_send(sql)
                
    def upload_comment(self, comment_len):
        comments_ins = []
        buffer = collections.deque()
        comment_id = 0
        buff_size = round(self.posts * 0.1)
        for _ in range(self.comments):
            user_id = random.randint(1, self.users)
            post_id = random.randint(1, self.posts)
            text = self.fake.sentence(random.randint(1, comment_len))
            for tmp in buffer:
                if post_id == tmp[1]:
                    comment_id = tmp[0]
                    break
                comment_id = 0
            if len(buffer) < buff_size:
                buffer.append((_+1, post_id))
            else:
                buffer.popleft()
            comments_ins.append("('{}', '{}', '{}', '{}')".format(post_id, user_id, comment_id, text))
            comment_id = 0
        comments_ins = ', '.join(comments_ins)
        sql = """Insert
                 Into Comment (Id_post, Id_user, Id_comment, Text)
                 Values"""
        sql = ' '.join((sql, comments_ins))
        self.db.sql_send(sql)
        
    def run(self):
        self.upload_users()
        self.upload_blogs()
        self.upload_posts()
        self.upload_comment(8)
        self.db.cursor.close()
        self.db.connection.close()

h = db_upload()
            
    
