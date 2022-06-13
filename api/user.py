import json
from flask import request
from flask_restx import Namespace, Resource, abort, fields
from api import RESPONSE
from models import db
from models.location import Location
from models.user import User
import pandas as pd
import copy

from util.password import check_password, pw_sha256

UserNamespace = Namespace(
    name = "User API",
    description = '유저 정보를 처리하기 위한 API입니다.'
)

user_create_model = UserNamespace.model('UserCreateModel', {
    'user_id': fields.Integer,
    'loc_id': fields.Integer,
})

user_response = UserNamespace.model('UserResponse',{
    'status': fields.String(description='Success Or Failed', required=True),
    'msg': fields.String(description='Detail Status message', required=True)
})

user_object_for_create = UserNamespace.model('UserObjectForCreate', {
    'name': fields.String,
    'password': fields.String,
    'phone': fields.String
})

location_object_for_create = UserNamespace.model('LocationObjectForCreate', {
    'dest': fields.String,
    'location': fields.String
})

user_create_request = UserNamespace.model('UserCreateRequest', {
    'user': fields.Nested(user_object_for_create),
    'loc': fields.Nested(location_object_for_create)
})

user_create_response = UserNamespace.inherit('UserCreateResponse', user_response, {
    'content': fields.Nested(user_create_model)
})

@UserNamespace.route('/<int:id>', doc={'params':{'id': 'user id'}})
class UserDeleteApi(Resource):
    def del_user(self, id, pw):
        response = copy.deepcopy(RESPONSE)

        if not check_password(id, pw):
            response['status'] = 'Failed'
            response['msg'] = 'Invalid Password'
            return response

        loc_deleted = Location.query.filter_by(user_id=id).delete()
        user_deleted = User.query.filter_by(id=id).delete()
        db.session.commit()

        if loc_deleted <= 0 or user_deleted <= 0:
            response['status'] = 'Failed'
            response['msg'] = 'Could not find user'
            return response

        response['msg'] = 'Succeeded to remove user data'
        return response
    
    @UserNamespace.param('pw', 'user password', required=True)
    @UserNamespace.response(200, 'Success', user_response)
    @UserNamespace.response(400, 'Bad Request')
    @UserNamespace.response(404, 'Failed', user_response)
    def delete(self, id):    
        '''해당하는 유저를 삭제합니다.'''
        if not 'pw' in request.args:
            abort(400, 'Bad Request')

        result = self.del_user(id, request.args.get('pw'))
        return result, 200 if result['status'] == 'Success' else 404

@UserNamespace.route('')
class UserInsertApi(Resource):    
    def add_user(self, user, loc):        
        response = copy.deepcopy(RESPONSE)

        if not 'name' in user or (user['name'].replace(' ', '') == ''):
            response['status'] = 'Failed'
            response['msg'] = 'user.name parameter is required.'
        elif not 'phone' in user or (user['phone'].replace(' ', '') == ''):
            response['status'] = 'Failed'
            response['msg'] = 'user.phone parameter is required.'
        elif not 'password' in user or (user['password'].replace(' ', '') == ''):
            response['status'] = 'Failed'
            response['msg'] = 'user.password parameter is required.'
        elif not 'dest' in loc or (loc['dest'].replace(' ', '') == ''):
            response['status'] = 'Failed'
            response['msg'] = 'loc.dest parameter is required.'
        elif not 'location' in loc or (loc['location'].replace(' ', '') == ''):
            response['status'] = 'Failed'
            response['msg'] = 'loc.location parameter is required.'
        
        if response['status'] == 'Failed':
            return response
        
        dbUser = User(name=user['name'], password=pw_sha256(user['password']), phone_number=user['phone'])
        
        db.session.add(dbUser)
        db.session.flush()
        
        dbLoc = Location(dbUser.id, loc['location'], loc['dest'])
        db.session.add(dbLoc)
        db.session.commit()

        response['content'] = {'user_id': dbUser.id, 'loc_id': dbLoc.id}
        return response

    @UserNamespace.doc(body=user_create_request)
    @UserNamespace.response(200, 'Success', user_create_response)
    @UserNamespace.response(400, 'Bad Request')
    @UserNamespace.response(404, 'Failed', user_response)
    def post(self):
        '''새 유저와 요청 정보를 생성합니다.'''
        if not 'user' in request.json or not 'loc' in request.json:
            abort(400, 'Bad Request')

        result = self.add_user(request.json['user'], request.json['loc'])
        return result, 200 if result['status'] == 'Success' else 404