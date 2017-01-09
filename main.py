import logging
from google.appengine.ext import ndb
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
        
        movies = model.Movie.get_movies()
        movies = [(movie.movie_title, movie.key.id()) for movie in movies ]
        data = {'movies': movies }
        path = os.path.join(os.path.dirname(__file__), 'templates/all_movies.html')
        self.render(path, data)
        

class MovieDetailHandler(RequestHandler):

    def get(self, movie_id):
        movie = model.Movie.get_by_id(int(movie_id))
        data = { 'movie': movie, 'movie_id': movie.key.id(), 'actor_id': movie.actor.id() }
        path = os.path.join(os.path.dirname(__file__), 'templates/movie_detail.html')
        self.render(path, data)

class SearchMovieHandler(RequestHandler):
    
    def post(self):
        
        title = self.request.get("title")
        movie = model.Movie.exiting_movie(title.lower())
        if movie:
            url = "/detail/{0}/".format(movie.key.id())
            self.redirect(url)
        else:
            data = {'message': "Movie not found"}
            path = os.path.join(os.path.dirname(__file__), 'templates/main.html')
            self.render(path, data)


class AddNewMovieHandler(RequestHandler):
    
    def _process(self, message=None, data =None):
        if data:
            data.update({ 
              'message': message,
            })
        else:
            data = {'message': message}
        path = os.path.join(os.path.dirname(__file__), 'templates/new_movie.html')
        self.render(path, data)

    def get(self, command=None):
        actors = model.Actor.get_actors()
        actors = [(actor.name, actor.key.id()) for actor in actors ]
        data = {'actors': actors}
        message = None
        self._process(message, data)

    def post(self, command):
        
        actors = model.Actor.get_actors()
        actors = [(actor.name, actor.key.id()) for actor in actors ]
        data = {'actors': actors}
        if command == 'add':
            website =  self.request.get("website").replace("http://","").replace("https://","")
            title = self.request.get("title")
            movie_exiting = model.Movie.exiting_movie(title.lower())
            actor_id = self.request.get("actor_id")
            actor = model.Actor.get_by_id(int(actor_id))
            if not movie_exiting:
                
                imagedata = model.ImageData()
                imagedata.name = self.request.get('title')
                imagedata.image = self.request.get('image')
                imagedata.put()
                movie = model.Movie(movie_title=title, cast= (self.request.get("cast")), \
                        plot= (self.request.get("plot")) ,  \
                        website= website ,enabled=True )
                movie.actor = actor.key
                movie.image=imagedata.key
                movie.put()
                self._process("The movie has been added successfully.", data)
            else:
                self._process('Movie title entered in already existing, change title name if you still want to add it', data)
        else:
            self._process("Unsupported command.", data)


class AddReviewHandler(RequestHandler):
    
    def post(self, movie_id):
        movie = model.Movie.get_by_id(int(movie_id))
        review = self.request.get("review")
        movie.reviews.append(review)
        movie.put()
        url = "/detail/{0}/".format(movie_id)
        self.redirect(url)
#         data = { 'movie': movie, 'movie_id': movie.key.id(), 'actor_id': movie.actor.id() }
#         path = os.path.join(os.path.dirname(__file__), 'templates/movie_detail.html')
#         self.render(path, data)

class ImageHandler(RequestHandler):
    def get(self, id):
        movie = model.Movie.get_by_id(int(id))
        actor = model.Actor.get_by_id(int(id))
        if movie and movie.image:
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(movie.image.get().image)
        elif actor and actor.image:
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(actor.image.get().image)

        else:
            self.error(404)


class DisableMovieHandler(RequestHandler):

    def get(self, movie_id):
        movie = model.Movie.get_by_id(int(movie_id))
        
        if not movie:
            self.error(404)
        movie.enabled = False
        movie.put()
        self.redirect('/')


class ListAllActorHandler(RequestHandler):
    def get(self):
        
        actors = model.Actor.get_actors()
        actors = [(actor.name, actor.key.id()) for actor in actors ]
        data = {'actors': actors }
        path = os.path.join(os.path.dirname(__file__), 'templates/all_actors.html')
        self.render(path, data)

class ActorDetailHandler(RequestHandler):

    def get(self, actor_id):
        actor = model.Actor.get_by_id(int(actor_id))
        movies = model.Movie.get_by_actor(actor.key)
        movies = [(movie.movie_title, movie.key.id()) for movie in movies ]
        data = {'movies': movies, 'actor': actor, 'actor_id': actor_id}
        path = os.path.join(os.path.dirname(__file__), 'templates/actor_detail.html')
        self.render(path, data)


class AddActorHandler(RequestHandler):
    
    def _process(self, message=None):
        data = { 
            'message': message,
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/new_actor.html')
        self.render(path, data)

    def get(self, command=None):
        self._process()

    def post(self, command):

        if command == 'add':
            website =  self.request.get("website").replace("http://","").replace("https://","")
            name = self.request.get("name")
            actor_exiting = model.Actor.get_by_name(name.lower())
            if not actor_exiting:
                
                imagedata = model.ImageData()
                imagedata.name = self.request.get('name')
                imagedata.image = self.request.get('image')
                imagedata.put()
                actor = model.Actor(name=name, about= (self.request.get("about")), \
                        website= website ,enabled=True )
                actor.image=imagedata.key
                actor.put()
            self._process("The actor has been added successfully.")
#             else:
#                 self._process('Movie title entered in already existing, change title name if you still want to add it')
        else:
            self._process("Unsupported command.")
            
class GivenActorMovies(RequestHandler):
    
    def get(self, actor_id):
        
        actor = model.Actor.get_by_id(int(actor_id)).key
        movies = model.Movie.get_by_actor(actor)
        movies = [(movie.movie_title, movie.key.id()) for movie in movies ]
        data = {'movies': movies}
        path = os.path.join(os.path.dirname(__file__), 'templates/all_movies.html')
        self.render(path, data)
        
        
class NotFound(RequestHandler):
    def get(self):
        self.error(404)


app = webapp.WSGIApplication( [
    ('/', HomeHandler),
    ('/list', ListAllMovieHandler),
    ('/new', AddNewMovieHandler),
    ('/new/(.*)/', AddNewMovieHandler),
    ('/detail/(.*)/', MovieDetailHandler),
    ('/addreview/(.*)/', AddReviewHandler),
    ('/listactors', ListAllActorHandler),
    ('/newactor', AddActorHandler),
    ('/newactor/(.*)/', AddActorHandler),
    ('/givenactormovie/(.*)/', GivenActorMovies),
    ('/actordetail/(.*)/', ActorDetailHandler),
    ('/searchmovie', SearchMovieHandler),
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

