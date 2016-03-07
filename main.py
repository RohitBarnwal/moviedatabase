import logging

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import model

import os


class RequestHandler(webapp.RequestHandler):
    
    def render(self, path, data=None):
        if data is None:
            data = {}
        self.response.out.write(template.render(path, data))

    def error( self, code ):
        webapp.RequestHandler.error( self, code )
        if code >= 500 and code <= 599:
            path = os.path.join(os.path.dirname(__file__), 'templates/50x.html')
            self.render(path)
        if code == 404:
            path = os.path.join(os.path.dirname(__file__), 'templates/404.html')
            self.render(path)


class HomeHandler(RequestHandler):
    def get(self):
        
        path = os.path.join(os.path.dirname(__file__), 'templates/main.html')
        self.render(path)


class ListAllMovieHandler(RequestHandler):
    def get(self):
        
        data = {'movies': model.Movie.get_movies()}
        path = os.path.join(os.path.dirname(__file__), 'templates/all_movies.html')
        self.render(path, data)
        

class MovieDetailHandler(RequestHandler):

    def get(self, key):
        movie = model.Movie.get(key)
        data = { 'movie': movie }
        path = os.path.join(os.path.dirname(__file__), 'templates/movie_detail.html')
        self.render(path, data)


class AddNewMovieHandler(RequestHandler):
    
    def _process(self, message=None):
        data = { 
          'message': message,
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/new_movie.html')
        self.render(path, data)

    def get(self, command=None):
        self._process()

    def post(self, command):

        if command == 'add':
            image = self.request.get("image")
            website =  self.request.get("website").replace("http://","")
            title = self.request.get("title")
            movie_exiting = model.Movie.exiting_movie(title)
            if not movie_exiting:
                movie = model.Movie(movie_title=title, cast= (self.request.get("cast")), \
                        plot= (self.request.get("plot")) , image=db.Blob(image), \
                        website= website ,enabled=True )
                movie.put()
                self._process("The movie has been added.")
            else:
                self._process('Movie title entered in already existing, change title name if you still want to add it')
        else:
            self._process("Unsupported command.")


class ImageHandler(RequestHandler):
    def get(self, id):
        movie = db.get(id)
        if movie.image:
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(movie.image)
        else:
            self.error(404)


class DisableMovieHandler(RequestHandler):

    def get(self, key):
        movie = model.Movie.get(key)
        
        if not movie:
            self.error(404)
        movie.enabled = False
        movie.put()
        self.redirect('/')

        
class NotFound(RequestHandler):
    def get(self):
        self.error(404)


app = webapp.WSGIApplication( [
    ('/', HomeHandler),
    ('/list', ListAllMovieHandler),
    ('/new', AddNewMovieHandler),
    ('/new/(.*)/', AddNewMovieHandler),
    ('/detail/(.*)/', MovieDetailHandler),
    ('/image/(.*)/', ImageHandler),
    ('/disable/(.*)/', DisableMovieHandler),
    ('/.*', NotFound),
  ],
  debug=True)

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(app)

if __name__ == "__main__":
    main()

