from google.appengine.ext import ndb


class Movie(ndb.Model):
    
    """Models an individual Movie entry."""
    created = ndb.DateTimeProperty(auto_now_add=True)
    movie_title = ndb.StringProperty()
    title_lower = ndb.ComputedProperty(lambda self: self.movie_title and self.movie_title.lower())
    actor = ndb.KeyProperty()
    website = ndb.StringProperty()
    plot = ndb.TextProperty()
    cast = ndb.TextProperty()
    image = ndb.KeyProperty()
    enabled = ndb.BooleanProperty()
    reviews = ndb.StringProperty(repeated=True)

    @staticmethod
    def get_movies():
        """
        Return list of movies added in database ordered by created date.
        If database size is large, use pagination while fetching from query.
        """
#         return Movie.all().filter( "enabled =", True ).order('-created').fetch(1000)
        return Movie.query(Movie.enabled==True).fetch()


    @staticmethod
    def exiting_movie(title):
        """
        No two movie with same title are allowed to be added. 
        Try adding with different title or disable the previous one.
        """
        movie_object = Movie.query(Movie.title_lower == title).get()
        if movie_object and movie_object.enabled:
            return movie_object
        return None

    @staticmethod
    def get_by_actor(actor_key):
        
        movies = Movie.query(Movie.actor==actor_key).fetch()
        
        return movies

class ImageData(ndb.Model):
     name = ndb.StringProperty(indexed=False)
     image = ndb.BlobProperty()


class Actor(ndb.Model):
    
    """Models an actor entry."""
    created = ndb.DateTimeProperty(auto_now_add=True)
    name = ndb.StringProperty()
    name_lower = ndb.ComputedProperty(lambda self: self.name and self.name.lower())
    website = ndb.StringProperty()
    about = ndb.TextProperty()
    image = ndb.KeyProperty()
    enabled = ndb.BooleanProperty()
    
    @staticmethod
    def get_by_name(name):
       
        actor = Actor.query().filter(Actor.name_lower == name).get()
        if actor and actor.enabled:
            return actor
        return None
    
    @staticmethod
    def get_actors():
        """
        Return list of actors added in database ordered by created date.
        If database size is large, use pagination while fetching from query.
        """
        return Actor.query(Actor.enabled==True).fetch()
