import os

from flask import Flask, request, jsonify, make_response
from transformation.generator_handler import GeneratorHandler
from transformation.generators.documents_output_generator import DocumentsOutputGenerator
from transformation.generators.generator_register import GeneratorRegister

from metamodel.model import Model
from transformation.data_manipulation import DataManipulation, VersionUnavailableError

def create_app(data_manipulation, handler):

    app =  Flask(__name__)
    app.config["DEBUG"] = True
    os.environ['PYTHONPATH'] = os.getcwd()


    @app.route('/', methods=['GET'])
    def home():
        model = data_manipulation.get_latest_model()
        json = model.to_json()
        return make_response(json, 200)


    @app.route('/model', methods=['GET', 'POST'])
    def model():
        if request.method == 'GET':
            try:
                content = data_manipulation.get_latest_model()
                return make_response(content.to_json(), 200)
            except VersionUnavailableError as version_error:
                return make_response(jsonify({"error": "Not found"}), 404)

        if request.method == 'POST':
            """modify/update model"""
            content = request.get_json()
            model = Model.from_json(content)
            data_manipulation.update_model(model)
            return make_response("CREATED", 201)


    @app.route('/models/<version_id>', methods=['GET'])
    def model_by_version(version_id):
        if request.method == 'GET':
            try:
                content = data_manipulation.get_model_by_version(version_id)
                return make_response(content.to_json(), 200)
            except VersionUnavailableError:
                return make_response(jsonify({"error": "Not found"}), 404)


    @app.route('/generators', methods=['GET', 'POST'])
    def generators():
        if request.method == 'GET':
            try:
                content = handler.generators.to_json()
                return make_response(content, 200)
            except:
                return make_response(jsonify({"error": "Not found"}), 404)

        if request.method == 'POST':
            """modify/update generator"""
            content = request.get_json()
            handler.generators = GeneratorRegister.from_json(content)
            return make_response("CREATED", 201)

    @app.route('/generators/<generator_id>', methods=['GET', 'POST'])
    def generator_by_id(generator_id):
        if request.method == 'GET':
            try:
                found_generator = handler.get_generator(int(generator_id))
                return make_response(found_generator.to_json(), 200)
            except KeyError:
                return make_response(jsonify({"error": "Not found"}), 404)

        elif request.method == 'POST':
            return make_response(jsonify({'error':'Not implemented'}), 501)

    @app.route('/table', methods=['GET', 'POST'])
    def element_generator_table():
        if request.method == 'GET':
            try:
                content = handler.element_generator_table.to_json()
                return make_response(content, 200)
            except Exception as e:
                print(e)
                return make_response(jsonify({"error": "Not found"}), 404)
        elif request.method == 'POST':
            try:
                content = request.get_json()
                handler.element_generator_table.from_json(content)
                return make_response("OK", 200)
            except:
                return make_response(jsonify({'error':'Bad request'}), 400)

    @app.route('/generation/<element_id>', methods = ['GET'])
    def generate_single_element(element_id):
        try:
            element = handler.element_generator_table.get_element_by_id(int(element_id))
            handler.generate_single_element(element)
            return make_response("OK", 200)
        except ValueError:
            return make_response(jsonify({'error': 'Bad request'}), 400)

    return app

if __name__ == '__main__':
    data_manipulation = DataManipulation()
    data_manipulation = data_manipulation.load_from_dill()
    handler = GeneratorHandler().load_from_dill()

    app = create_app(data_manipulation, handler)
    app.run(use_reloader=False)