from google.appengine.ext import db


class Movie(db.Model):
    
    """Models an individual Movie entry."""
    created = db.DateTimeProperty(auto_now_add=True)
    movie_title = db.StringProperty()
    website = db.StringProperty()
    plot = db.TextProperty()
    cast = db.TextProperty()
    image = db.BlobProperty()
    enabled = db.BooleanProperty()
    

    @staticmethod
    def get_movies():
        """
        Return list of movies added in database ordered by created date, maximum 1000. If database size is large, use pagination.
        """
        return Movie.all().filter( "enabled =", True ).order('-created').fetch(1000)


    @staticmethod
    def exiting_movie(title):
        """
        No two movie with same title are allowed to added, add year of release in case of same title or disable the previous one.
        """
        movie_object = Movie.all().filter( "movie_title =", title ).get()
        if movie_object and movie_object.enabled:
            return True
        return False
