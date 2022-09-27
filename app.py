# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
api = Api(app)

movie_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_ns = api.namespace('genres')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False}

db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String()
    description = fields.String()
    trailer = fields.String()
    year = fields.Integer()
    rating = fields.Float()
    genre_id = fields.Integer()
    genre = fields.String()
    director_id = fields.Integer()
    director = fields.String()


class DirectorSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()


class GenreSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movie_ns.route('/')
class MovieView(Resource):
    def get(self):
        directors_id = request.args.get('directors_id')
        genre_id = request.args.get('genre_id')
        result = db.session.query(Movie)
        if directors_id:
            result = result.filter(Movie.director_id == directors_id)
        if genre_id:
            result = result.filter(Movie.genre_id == genre_id)
        end_result = movies_schema.dump(result)
        if len(end_result) != 0:
            return end_result, 200
        else:
            return 'Wrong response', 404

    def post(self):
        data = request.json
        new_movies = Movie(**data)
        with db.session.begin():
            db.session.add(new_movies)
        return 'new data added', 201


@movie_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid):
        searched_movie = db.session.query(Movie).get(uid)
        result = movie_schema.dump(searched_movie)
        return result, 200

    def put(self, uid):
        with db.session.begin():
            request_data = request.json
            edited_movie = db.session.query(Movie).get(uid)
            edited_movie.title = request_data.get('title')
            edited_movie.description = request_data.get('description')
            edited_movie.trailer = request_data.get('trailer')
            edited_movie.year = request_data.get('year')
            edited_movie.rating = request_data.get('rating')
            edited_movie.genre_id = request_data.get('genre_id')
            edited_movie.director_id = request_data.get('director_id')
            db.session.add(edited_movie)
        return f'Movie edited'

    def delete(self, uid):
        with db.session.begin():
            db.session.query(Movie).filter(Movie.id == uid).delete()
        return 'Movie removed'


@directors_ns.route('/')
class DirectorView(Resource):
    def get(self):
        result = db.session.query(Director).all()
        return directors_schema.dump(result), 200

    def post(self):
        data = request.json
        new_directors = Director(**data)
        with db.session.begin():
            db.session.add(new_directors)
        return 'new data added', 201


@directors_ns.route('/<int:uid>')
class DirectorView(Resource):
    def get(self, uid):
        result = db.session.query(Director).get(uid)
        return genre_schema.dump(result), 200

    def delete(self, uid):
        with db.session.begin():
            db.session.query(Director).filter(Director.id == uid).delete()
        return 'director removed'

    def put(self, uid):
        with db.session.begin():
            edited_director = db.session.query(Director).get(uid)
            data = request.json
            edited_director.name = data.get('name')
            db.session.add(edited_director)
        return 'director edited', 204


@genres_ns.route('/')
class GenresView(Resource):
    def get(self):
        result = db.session.query(Genre).all()
        return genres_schema.dump(result)

    def post(self):
        data = request.json
        new_genres = Genre(**data)
        with db.session.begin():
            db.session.add(new_genres)
        return 'new data added', 201


@genres_ns.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid):
        result = db.session.query(Genre).get(uid)
        return genre_schema.dump(result)

    def delete(self, uid):
        with db.session.begin():
            db.session.query(Genre).filter(Genre.id == uid).delete()
        return 'genre removed'

    def put(self, uid):
        with db.session.begin():
            edited_genre = db.session.query(Genre).get(uid)
            data = request.json
            edited_genre.name = data.get('name')
            db.session.add(edited_genre)
        return 'genre edited', 204


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
