import os
import json

from flask import Flask, request, jsonify, make_response, render_template
from transformation.generator_handler import GeneratorHandler
from transformation.generators.generator_register import GeneratorRegister
from tracing.tracer import Tracer
from metamodel.model import Model
from transformation.data_manipulation import DataManipulation, VersionUnavailableError
from validation_flow_handler import extend


def create_app(data_manipulation=None, handler=None, tracer=None):
    app = Flask(__name__, template_folder='templates')
    app.config["DEBUG"] = True
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    os.environ['PYTHONPATH'] = os.getcwd()

    data_manipulation, handler, tracer = initialize(data_manipulation, handler, tracer)

    @app.errorhandler(404)
    def not_found(e):
        return render_template('app/404.html')

    @app.route('/', methods=['GET'])
    @app.route('/home', methods=['GET'])
    def home():
        return render_template('app/index.html')

    @app.route('/model', methods=['GET', 'POST'])
    def model():
        if request.method == 'GET':
            try:
                content_json = data_manipulation.get_latest_model().to_json()
                return render_template('app/model.html', model=content_json)

            except VersionUnavailableError as version_error:
                return make_response(render_template('app/404.html'), 404)

        if request.method == 'POST':
            """modify/update model"""
            content = request.get_json()
            model_ = Model.from_json(content)
            data_manipulation.update_model(model_)
            return make_response("CREATED", 201)

    @app.route('/models/<version_id>', methods=['GET'])
    def model_by_version(version_id):
        if request.method == 'GET':
            try:
                content_json = data_manipulation.get_model_by_version(version_id).to_json()
                return render_template('app/model.html', model=content_json, version_id=version_id)
            except VersionUnavailableError:
                return make_response(render_template('app/404.html'), 404)

    @app.route('/generators', methods=['GET', 'POST'])
    def generators():
        if request.method == 'GET':
            try:
                content_json = handler.generators.to_json()
                return render_template('app/generator.html', generator=content_json)
            except:
                return make_response(render_template('app/404.html'), 404)

        if request.method == 'POST':
            """modify/update generator"""
            content = request.get_json()
            handler.generators = GeneratorRegister.from_json(content)
            return make_response("CREATED", 201)

    @app.route('/generators/<generator_id>', methods=['GET', 'POST'])
    def generator_by_id(generator_id):
        if request.method == 'GET':
            try:
                content_json = handler.get_generator(int(generator_id)).to_json()
                return render_template('app/generator.html', generator=content_json, generator_id=generator_id)
            except KeyError:
                return make_response(render_template('app/404.html'), 404)

        elif request.method == 'POST':
            return make_response(jsonify({'error': 'Not implemented'}), 501)

    @app.route('/table', methods=['GET', 'POST'])
    def element_generator_table():
        if request.method == 'GET':
            try:
                content = handler.element_generator_table.to_json()
                return render_template('app/element_generator_table.html', table=content)
            except Exception as e:
                return make_response(render_template('app/404.html'), 404)

        elif request.method == 'POST':
            try:
                content = request.get_json()
                handler.element_generator_table.register_from_json(content)
                return make_response("OK", 200)
            except:
                return make_response(jsonify({'error': 'Bad request'}), 400)

    @app.route('/tracer', methods=['GET', 'POST'])
    def tracer():
        if request.method == 'GET':
            try:
                content = tracer.to_json()
                return render_template('app/tracer.html', tracer=content)
            except Exception as e:
                return make_response(render_template('app/404.html'), 404)

        elif request.method == 'POST':
            try:
                content = request.get_json()
                tracer.register_from_json(content)
                return make_response("OK", 200)
            except:
                return make_response(jsonify({'error': 'Bad request'}), 400)

    @app.route('/generation/<element_id>', methods=['GET'])
    def generate_single_element(element_id):
        try:
            element_id = handler.element_generator_table.get_element_by_id(int(element_id))
            handler.generate_single_element(data_manipulation.get_element_by_id(element_id), data_manipulation)
            return make_response("OK", 200)
        except ValueError:
            return make_response(jsonify({'error': 'Bad request'}), 400)

    @app.route('/diff_generation/all', methods=['GET'])
    def generate_all_elements():
        try:
            handler.generate_by_diff_generator(data_manipulation, 0, "../../files/")
            return make_response("OK", 200)
        except ValueError:
            return make_response(jsonify({'error': 'Bad request'}), 400)

    return app


def initialize(data_manipulation=None, handler=None, tracer=None):
    for generator in handler.generators.values():
        generator.tracer = tracer
    return data_manipulation, handler, tracer


def main():
    data_manipulation = DataManipulation()
    data_manipulation = data_manipulation.load_from_json()
    handler = GeneratorHandler().load_from_json()
    tracer = Tracer().load_from_json()
    app = create_app(data_manipulation, handler, tracer)
    app = extend(app, data_manipulation, handler, tracer)
    app.run(use_reloader=False)


if __name__ == '__main__':
    main()
