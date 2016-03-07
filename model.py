from google.appengine.ext import db


class Movie(db.Model):
    
    """Models an individual Movie entry."""
    created = db.DateTimeProperty(auto_now_add=True)
    movie_title = db.StringProperty()
    title_lower = db.ComputedProperty(lambda self: self.movie_title and self.movie_title.lower())

    website = db.StringProperty()
    plot = db.TextProperty()
    cast = db.TextProperty()
    image = db.BlobProperty()
    enabled = db.BooleanProperty()
    

    @staticmethod
    def get_movies():
        """
        Return list of movies added in database ordered by created date, maximum 1000. 
        If database size is large, use pagination while fetching from query.
        """
        return Movie.all().filter( "enabled =", True ).order('-created').fetch(1000)


    @staticmethod
    def exiting_movie(title):
        """
        No two movie with same title are allowed to be added. 
        Try adding with different title or disable the previous one.
        """
        movie_object = Movie.all().filter( "title_lower =", title ).get()
        if movie_object and movie_object.enabled:
            return True
        return False
