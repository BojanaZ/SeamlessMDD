import os

from flask import Flask, request, jsonify, make_response
from transformation.generator_handler import GeneratorHandler
from transformation.generators.generator_register import GeneratorRegister

from metamodel.model import Model
from transformation.data_manipulation import DataManipulation, VersionUnavailableError


def create_app(data_manipulation_=None, handler_=None):
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    os.environ['PYTHONPATH'] = os.getcwd()
    if data_manipulation_ is None:
        data_manipulation_ = DataManipulation()
        data_manipulation_ = data_manipulation_.load_from_json()

    if handler_ is not None:
        handler_ = GeneratorHandler().load_from_json()

    @app.route('/', methods=['GET'])
    def home():
        model_ = data_manipulation_.get_latest_model()
        response = make_response(model_.to_json(), 200)
        response.headers['Content-type'] = "application/json"
        return response

    @app.route('/model', methods=['GET', 'POST'])
    def model():
        if request.method == 'GET':
            try:
                content = data_manipulation_.get_latest_model()
                response = make_response(content.to_json(), 200)
                response.headers['Content-type'] = "application/json"
                return response

            except VersionUnavailableError as version_error:
                return make_response(jsonify({"error": "Not found"}), 404)

        if request.method == 'POST':
            """modify/update model"""
            content = request.get_json()
            model_ = Model.from_json(content)
            data_manipulation_.update_model(model_)
            return make_response("CREATED", 201)

    @app.route('/models/<version_id>', methods=['GET'])
    def model_by_version(version_id):
        if request.method == 'GET':
            try:
                content = data_manipulation_.get_model_by_version(version_id)
                response = make_response(content.to_json(), 200)
                response.headers['Content-type'] = "application/json"
                return response
            except VersionUnavailableError:
                return make_response(jsonify({"error": "Not found"}), 404)

    @app.route('/generators', methods=['GET', 'POST'])
    def generators():
        if request.method == 'GET':
            try:
                content = handler_.generators.to_json()
                response = make_response(content, 200)
                response.headers['Content-type'] = "application/json"
                return response
            except:
                return make_response(jsonify({"error": "Not found"}), 404)

        if request.method == 'POST':
            """modify/update generator"""
            content = request.get_json()
            handler_.generators = GeneratorRegister.from_json(content)
            return make_response("CREATED", 201)

    @app.route('/generators/<generator_id>', methods=['GET', 'POST'])
    def generator_by_id(generator_id):
        if request.method == 'GET':
            try:
                found_generator = handler_.get_generator(int(generator_id))
                response = make_response(found_generator.to_json(), 200)
                response.headers['Content-type'] = "application/json"
                return response
            except KeyError:
                return make_response(jsonify({"error": "Not found"}), 404)

        elif request.method == 'POST':
            return make_response(jsonify({'error':'Not implemented'}), 501)

    @app.route('/table', methods=['GET', 'POST'])
    def element_generator_table():
        if request.method == 'GET':
            try:
                content = handler_.element_generator_table.to_json()
                response = make_response(content, 200)
                response.headers['Content-type'] = "application/json"
                return response
            except Exception as e:
                print(e)
                return make_response(jsonify({"error": "Not found"}), 404)
        elif request.method == 'POST':
            try:
                content = request.get_json()
                handler_.element_generator_table.register_from_json(content)
                return make_response("OK", 200)
            except:
                return make_response(jsonify({'error': 'Bad request'}), 400)

    @app.route('/generation/<element_id>', methods=['GET'])
    def generate_single_element(element_id):
        try:
            element_id = handler_.element_generator_table.get_element_by_id(int(element_id))
            handler_.generate_single_element(data_manipulation_.get_element_by_id(element_id), data_manipulation_)
            return make_response("OK", 200)
        except ValueError:
            return make_response(jsonify({'error': 'Bad request'}), 400)

    return app


if __name__ == '__main__':
    data_manipulation = DataManipulation()
    data_manipulation = data_manipulation.load_from_json()
    handler = GeneratorHandler().load_from_json()

    app = create_app(data_manipulation, handler)
    app.run(use_reloader=False)
