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
        for _ in range(self.users):
            login = self.gen_login()
            password = self.fake.password(8)
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            self.db.add_user(login, password, first_name, last_name)
        self.users_login.clear()
    
    def upload_blogs(self):
        for _ in range(self.blogs):
            user_id = random.randint(1, self.users)
            name_blog = self.fake.company()
            if user_id not in self.user_blog.keys():
                self.user_blog[user_id] = [_+1]
            else:
                self.user_blog[user_id].append(_+1)
            description = ''.join(self.fake.paragraph(2))
            sql = """Insert
                     Into Blog (Id_user, Name, Description)
                     Values ('{}', '{}', '{}');""".format(user_id, name_blog, description)
            self.db.sql_send(sql)
            
    def upload_posts(self):
        users_id = list(self.user_blog.keys())
        for _ in range(self.posts):
            user_id = random.choice(users_id)
            if len(self.user_blog[user_id]) > 1:
                blog_id = random.choice(self.user_blog[user_id])
            else:
                blog_id = self.user_blog[user_id][0]
            name_post = self.fake.sentence(random.randint(1,6))
            text_post = self.fake.text(random.randint(100, 600))
            sql = """Insert
                     Into Post (Id_user, Name, Text)
                     Values ('{}', '{}', '{}')""".format(user_id, name_post, text_post)
            self.db.sql_send(sql)
            sql = """Insert
                     Into Blog_Post (Id_blog, Id_post)
                     Values('{}', '{}');""".format(blog_id, _+1)
            self.db.sql_send(sql)
            
    def choice_rand_comment_id(self, post_id):
        sql = """Select Id
                 From Comment
                 where Id_post = '{}'""".format(post_id)
        ans = self.db.sql_send(sql)
        comment_id = []
        if len(ans):
            for res in ans:
                comment_id.append(res['Id'])
            return random.choice(comment_id)
        return 0
                
    def upload_comment(self, comment_len):
        for _ in range(self.comments):
            user_id = random.randint(1, self.users)
            post_id = random.randint(1, self.posts)
            text = self.fake.sentence(random.randint(1, comment_len))
            if random.randint(1,4) == 1:
                comment_id = self.choice_rand_comment_id(post_id)
            else:
                comment_id = 0
            sql = """Insert
                     Into Comment (Id_post, Id_user, Id_comment, Text)
                     Values('{}', '{}', '{}', '{}')""".format(post_id, user_id, comment_id, text)
            self.db.sql_send(sql)
        
    def run(self):
        self.upload_users()
        self.upload_blogs()
        self.upload_posts()
        self.upload_comment(8)
        self.db.cursor.close()
        self.db.connection.close()

h = db_upload()
