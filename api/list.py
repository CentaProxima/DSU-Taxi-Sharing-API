import copy
import json
import pandas as pd
from flask import request
from flask_restx import Namespace, Resource, fields
from api import RESPONSE
from models.location import Location
from models.user import User

ListNamespace = Namespace(
    name='List API',
    description='현재 존재하는 공유 택시 목록 요청을 위한 API 입니다.'
)

row_model = ListNamespace.model('ListRowModel', {
    'id': fields.Integer,
    'user_id': fields.Integer,
    'location': fields.String,
    'dest': fields.String,
    'create_at': fields.Integer,
    'name': fields.String,
    'phone_number': fields.String
})

list_model = ListNamespace.model('ListModel', {
    'rows': fields.List(fields.Nested(row_model)),
    'count': fields.Integer,
    'n_offset': fields.Integer,
    'total': fields.Integer
})

list_response = ListNamespace.model('ListReponse', {
    'status': fields.String,
    'msg': fields.String,
    'content': fields.Nested(list_model)
})

@ListNamespace.route('')
class SharingList(Resource):
    def list_share_info(self, count = 10, offset=0):
        response = copy.deepcopy(RESPONSE)
        query = Location.query\
            .join(User, Location.user_id == User.id)\
            .order_by(Location.create_at.desc())\
            .add_columns(User.name, User.phone_number)
        total_count = query.count()
        
        query = query.offset(offset).limit(count)
        df = pd.read_sql(query.statement, query.session.bind)
        rows = json.loads(df.to_json(orient='records'))        
        
        response['content'] =  {
            'rows': rows if type(rows) is list else [rows],
            'count': count,
            'n_offset': offset+count,
            'total': total_count
        }
        return response

    @ListNamespace.param('count', 'count to display result', type=int, default=10)
    @ListNamespace.param('offset', 'index to start querying', type=int, default=0)
    @ListNamespace.response(200, 'Success', list_response)
    def get(self):
        '''공유 택시 요청 목록을 가져옵니다.'''
        count = 10 if not 'count' in request.args else int(request.args.get('count'))
        offset = 0 if not 'offset' in request.args else int(request.args.get('offset'))
        return self.list_share_info(count, offset), 200
