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
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
							   autoescape = True)

class BlogPost(db.Model):
	title = db.StringProperty(required = True)
	body = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class MainHandler(Handler):
    def get(self):
        self.redirect("/blog")

class BlogHandler(Handler):
	def get(self):
		posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5")
		self.render("blog.html", posts = posts)

class NewPostHandler(Handler):
	def get(self):
		self.render("newpost.html")

	def post(self):
		title = self.request.get("title")
		body = self.request.get("body")


		if body and title:
			p = BlogPost(title = title, body = body)
			p.put()

			self.redirect("/blog/%s" % p.key().id())
		else:
			error = "Title and body required."
			self.render("newpost.html", title = title, body = body, error = error)

class ViewPostHandler(Handler):
	def get(self, id):
		if id.isdigit():
			post = BlogPost.get_by_id(int(id))
		else:
			self.redirect("/")

		if post:
			self.render("viewpost.html",post = post)
		else:
			self.redirect("/")

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', BlogHandler),
    ('/newpost', NewPostHandler),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
