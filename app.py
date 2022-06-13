import json
from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from api.search import SearchNamespace
from models import db
from api.list import ListNamespace
from api.user import UserNamespace

config = json.load(open('config.json', 'r'))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config['db_url']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config['db_track_modifications']

CORS(app, resources={r'*': {'origins': ['http://dsutaxi.ml', 'http://localhost:3000']}})

api = Api(
    app,
    version='1.0',
    title='동서대학교 공유택시 API',
    description='Taxi Sharing Service API for Dongseo University',
    terms_url='/',
    contact='20201637@office.dongseo.ac.kr',
    license='Dongseo University'
)
db.init_app(app)

api.add_namespace(UserNamespace, '/api/taxi/user')
api.add_namespace(ListNamespace, '/api/taxi/list')
api.add_namespace(SearchNamespace, '/api/taxi/search')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8443, debug=True)
