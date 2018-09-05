#!/usr/bin/python
import re
import uuid
import json

import flask
from flask import Flask
from flask import request
from flask import url_for
from flask import jsonify

app = Flask(__name__)
user_resource_file = '/home/pratik.saha/user_resource.json'


def scim_error(message, status_code=500):
    rv = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        "detail": message,
        "status": str(status_code)
    }
    return flask.jsonify(rv), status_code


@app.route('/_status', methods=['GET'])
def status(status_message='OK', status_code=200):
    status_dict = {
        'status': status_message,
    }

    return jsonify(status_dict), status_code


@app.route("/scim/Users/<user_id>", methods=['GET'])
def user_get(user_id):
    try:
        with open(user_resource_file) as fp:
            user_resources = json.load(fp)
    except ValueError:
        user_resources = []
    for resource in user_resources:
        if resource['id'] == user_id:
            return jsonify(resource)
    return scim_error("User not found", 404)


@app.route("/scim/Users", methods=['POST'])
def users_post():
    user_resource = request.get_json(force=True)
    print(user_resource)
    user_resource['id'] = str(uuid.uuid4())

    try:
        with open(user_resource_file) as fp:
            user_resources = json.load(fp)
    except ValueError:
        user_resources = []

    user_resources.append(user_resource)

    with open(user_resource_file, 'w+') as fp:
        json.dump(user_resources, fp)

    resp = flask.jsonify(user_resource)
    resp.headers['Location'] = url_for('user_get',
                                       user_id=user_resource['id'],
                                       _external=True)
    return resp, 201


@app.route("/scim/Users/<user_id>", methods=['PATCH'])
def users_patch(user_id):
    patch_resource = request.get_json(force=True)
    print(patch_resource)
    for attribute in ['schemas', 'Operations']:
        if attribute not in patch_resource:
            message = "Payload must contain '{}' attribute.".format(attribute)
            return message, 400
    schema_patchop = 'urn:ietf:params:scim:api:messages:2.0:PatchOp'
    if schema_patchop not in patch_resource['schemas']:
        return "The 'schemas' type in this request is not supported.", 501
    for operation in patch_resource['Operations']:
        if 'op' not in operation and operation['op'] != 'Replace':
            continue
        if '.' in operation['path']:
            key, nested_key = operation['path'].split('.')
            try:
                with open(user_resource_file) as fp:
                    user_resources = json.load(fp)
            except ValueError:
                user_resources = []
            
            value = operation['value']
            for key in value.keys():
                print(key)
    return jsonify({})


@app.route("/scim/Users", methods=['GET'])
def users_get():
    try:
        with open(user_resource_file) as fp:
            user_resources = json.load(fp)
    except ValueError:
        user_resources = []
    request_filter = request.args.get('filter')
    match = None
    print(request_filter)
    if request_filter:
        match = re.match('(\w+) eq "([^"]*)"', request_filter)
    if match:
        (search_key_name, search_value) = match.groups()
        for resource in user_resources:
            if resource[search_key_name] == search_value:
                user_resources = resource
                break
            else:
                return scim_error("User not found", 404)
    rv = {'schemas': ['urn:ietf:params:scim:api:messages:2.0:ListResponse'], "Resources": user_resources}
    return flask.jsonify(rv)


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
