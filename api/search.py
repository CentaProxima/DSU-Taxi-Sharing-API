from copy import deepcopy
import json
from api import RESPONSE
from flask import request
from flask_restx import Namespace, Resource, fields
from models.location import Location
from models.user import User
import pandas as pd

SearchNamespace = Namespace(
    name="Search API",
    description="검색 API 입니다."
)

response_model = SearchNamespace.model('SearchResponse',{
    'status': fields.String,
    'msg': fields.String
})

search_model = SearchNamespace.model('SearchModel',{
    'id': fields.Integer,
    'user_id': fields.Integer,
    'location': fields.String,
    'dest': fields.String,
    'create_at': fields.Integer,
    'name': fields.String,
    'phone_number': fields.String
})

search_content_model = SearchNamespace.model('SearchContentModel',{
    'rows': fields.List(fields.Nested(search_model)),
    'n_offset': fields.Integer,
    'count': fields.Integer,
    'total': fields.Integer
})

search_response_model = SearchNamespace.inherit('', response_model, {
    'content': fields.Nested(search_content_model)
})

@SearchNamespace.route('')
class Search(Resource):
    def search(self, _type, q, offset, count):
        resp = deepcopy(RESPONSE)
        
        if q is None:
            resp['status'] = 'Failed'
            resp['msg'] = 'q is required'
            return resp
        
        query = Location.query\
            .join(User, Location.user_id == User.id)\
            .add_columns(User.name, User.phone_number)

        if _type == 'user_id':
            query = query.filter(User.id == int(q))
        elif _type == 'name':
            query = query.filter(User.name.like('%'+q+'%')) 
        elif _type == 'source':
            query = query.filter(Location.location.like('%'+q+'%'))
        elif _type == 'dest':
            query = query.filter(Location.dest.like('%'+q+'%'))
        else:
            resp['status'] = 'Failed'
            resp['msg'] = 'Invalid type'
            return resp
        
        total = query.count()
        query = query.offset(offset).limit(count)
        df = pd.read_sql(query.statement, query.session.bind)
        rows = json.loads(df.to_json(orient='records'))

        resp['content'] = {
            'rows': rows if type(rows) is list else [rows],
            'n_offset': (offset+1)*count,
            'count': count,
            'total': total
        }
        return resp
    
    @SearchNamespace.param('type', 'search type', enum=['user_id', 'name', 'source', 'dest'], default='user_id')
    @SearchNamespace.param('q', 'search data', required=True)
    @SearchNamespace.param('offset', 'search start offset', default=0, type=int)
    @SearchNamespace.param('count', 'search data count', default=10, type=int)
    @SearchNamespace.response(200, 'Success', search_response_model)
    @SearchNamespace.response(404, 'Failed', response_model)
    def get(self):
        '''공유 택시 검색 API'''
        type = 'user_id' if not 'type' in request.args else request.args.get("type")
        q = None if not 'q' in request.args else request.args.get('q')
        offset = 0 if not 'offset' in request.args else int(request.args.get('offset'))
        count = 10 if not 'count' in request.args else int(request.args.get('count'))

        result = self.search(type, q, offset, count)
        return result, 404 if result['status'] == 'Failed' else 200