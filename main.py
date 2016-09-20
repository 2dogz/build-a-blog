import os
import webapp2
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                            autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Art(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def get(self):
        self.redirect('/newpost')
class NewPost(MainPage):
    def render_front(self, title="", art="", error=""):
        arts = db.GqlQuery("SELECT * FROM Art "
                            "ORDER BY created DESC ")

        self.render("front.html", title=title, art=art, error=error, arts=arts)

    def get(self):
        self.render_front()
    def post(self):

        title = self.request.get("title")
        art = self.request.get("art")

        if title and art:
            a = Art(title = title, art = art)
            # create "a" as a new instance in DB
            a.put()
            id = a.key().id()
            self.redirect("/blog/%s" % id)
        else:
            error = "we need both a title and some content!"
            self.render_front(title, art, error = error)
class BlogPage(NewPost):
    """handles request in the /blog part of my site"""
    def render_blog(self, title="", art="", error=""):
        arts = db.GqlQuery("SELECT * FROM Art "
                            "ORDER BY created DESC "
                            "Limit 5;")
        self.render("blog.html", title=title, art=art, error=error, arts=arts)

    def get(self):
        self.render_blog()
class ViewPostHandler(Handler):
    def get(self, post_id):
        pidi = int(post_id)
        post = Art.get_by_id(pidi)
        if post:
            self.render("singlepost.html", title=post.title, art=post.art)
        self.response.write(Art.get_by_id(pidi))
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', NewPost),
    ('/blog', BlogPage),
    webapp2.Route('/blog/<post_id:\d+>', ViewPostHandler)
], debug=True)
