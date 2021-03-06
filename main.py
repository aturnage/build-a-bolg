#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import webapp2
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)
    
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class PostWrite(db.Model):
    name = db.StringProperty(required = True)
    guestpost = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM PostWrite ORDER BY created DESC LIMIT 5")
        self.render('mainpage.html', posts = posts)

class Blog(Handler):
    def get(self):
        self.render("blog.html", name, guestpost, posts)

class NewPost(Handler):
    def get(self, name = "", guestpost = "", error = ""):
        self.render('newpostpage.html', name = name, guestpost = guestpost, error = error)

    def post(self):
        name = self.request.get("name")
        guestpost = self.request.get("guestpost")
        # logging.info(name)
        # logging.info(guestpost)
        if name and guestpost:
            a = PostWrite(name = name, guestpost = guestpost)
            # Puts the retrieved data in the datatbase
            a.put()

            self.redirect('/')
        else:
            error = "We need both a name and a post"
            self.get(name, guestpost, error)
            return

class BlogID(Handler):

    def get(self, blog_id):
        submission = PostWrite.get_by_id(int(blog_id))

        if submission:
            self.render("blog.html", submission=submission)

        else:
            error = "There is no blog post with that ID."
            self.render("blog.html", error=error)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<blog_id:\d+>', BlogID)
    ], debug=True)
