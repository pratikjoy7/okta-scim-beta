#!/usr/bin/python
import uuid
import json

import flask
from flask import Flask
from flask import request
from flask import url_for
from flask import jsonify

app = Flask(__name__)
user_resource_file = '/home/pratik.saha/user_resource.json'


def to_scim_list_resource(total_results, start_index):
    rv = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
        "totalResults": total_results,
        "startIndex": start_index,
        "Resources": []
    }
    return rv


def scim_error(message, status_code=500):
    rv = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        "detail": message,
        "status": str(status_code)
    }
    return flask.jsonify(rv), status_code


def render_json(obj):
    rv = obj.to_scim_resource()
    return flask.jsonify(rv)


@app.route('/_status', methods=['GET'])
def status(status_message='OK', status_code=200):
    status_dict = {
        'status': status_message,
    }

    return jsonify(status_dict), status_code


@app.route("/scim/Users", methods=['POST'])
def users_post():
    print(request.__dict__)

    user_resource = request.get_json(force=True)
    user_resource['id'] = str(uuid.uuid4())

    with open(user_resource_file, 'a+') as fp:
        json.dump(user_resource, fp)

    resp = flask.jsonify(user_resource)
    resp.headers['Location'] = url_for('user_get',
                                       user_id=user_resource['id'],
                                       _external=True)
    return resp, 201


# @app.route("/scim/Users/<user_id>", methods=['PUT'])
# def users_put(user_id):
#     user_resource = request.get_json(force=True)
#     user = User.query.filter_by(id=user_id).one()
#     user.update(user_resource)
#     db.session.add(user)
#     db.session.commit()
#     return render_json(user)


# @app.route("/scim/Users/<user_id>", methods=['PATCH'])
# def users_patch(user_id):
#     patch_resource = request.get_json(force=True)
#     print(patch_resource)
#     for attribute in ['schemas', 'Operations']:
#         if attribute not in patch_resource:
#             message = "Payload must contain '{}' attribute.".format(attribute)
#             return message, 400
#     schema_patchop = 'urn:ietf:params:scim:api:messages:2.0:PatchOp'
#     if schema_patchop not in patch_resource['schemas']:
#         return "The 'schemas' type in this request is not supported.", 501
#
#     for operation in patch_resource['Operations']:
#         if 'op' not in operation and operation['op'] != 'replace':
#             continue
#         value = operation['value']
#         for key in value.keys():
#             setattr(user, key, value[key])
#     db.session.add(user)
#     db.session.commit()
#     return render_json(user)


@app.route("/scim/Users", methods=['GET'])
def users_get():
    # request_filter = request.args.get('filter')
    # match = None
    # if request_filter:
    #     match = re.match('(\w+) eq "([^"]*)"', request_filter)
    # if match:
    #     (search_key_name, search_value) = match.groups()
    #     search_key = getattr(User, search_key_name)
    #     query = query.filter(search_key == search_value)
    with open(user_resource_file) as fp:
        user_resource = json.load(fp)

    total_results = None
    for resource in user_resource['Resources']:
        total_results = len(resource)

    start_index = int(request.args.get('startIndex', 1))
    if start_index < 1:
        start_index = 1
    start_index -= 1
    rv = to_scim_list_resource(total_results, start_index)
    rv['resources'] =
    return flask.jsonify(rv)


# @app.route("/scim/Groups", methods=['GET'])
# def groups_get():
#     rv = ListResponse([])
#     return flask.jsonify(rv.to_scim_resource())
#
#
# @app.route("/scim/Groups", methods=['POST'])
# def groups():
#     group_resource = request.get_json(force=True)
#     print(json.dumps(group_resource))
#
#     return 201


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
