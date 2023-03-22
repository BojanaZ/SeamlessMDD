import os
import shutil

from flask import Flask, request, jsonify, make_response, render_template, redirect
from transformation.generator_handler import GeneratorHandler
from transformation.generators.generator_register import GeneratorRegister
from tracing.tracer import Tracer
from metamodel.model import Model
from transformation.data_manipulation import DataManipulation, VersionUnavailableError
from transformation.conflict_resolution.question import Question


def create_app(data_manipulation=None, handler=None, tracer=None ):
    app = Flask(__name__, template_folder='templates')
    app.config["DEBUG"] = True
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    os.environ['PYTHONPATH'] = os.getcwd()

    data_manipulation, handler, tracer = initialize(data_manipulation, handler, tracer)
    question_preview_pairs = []

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

    @app.route('/generation-results', methods=['GET'])
    def get_generation_results():
        return render_template("app/generation_results.html", question_preview_pairs=question_preview_pairs)

    @app.route('/generation/<element_id>', methods=['GET'])
    def generate_single_element(element_id):
        return generate_preview_single_element(element_id, True)

    @app.route('/preview/all', methods=['GET'])
    def preview_all_elements():
        return generate_preview_all_elements(False)

    @app.route('/preview/<element_id>', methods=['GET'])
    def preview_single_element(element_id):
        return generate_preview_single_element(element_id, False)

    @app.route('/diff_generation/all', methods=['GET'])
    def generate_all_elements():
        return generate_preview_all_elements(True)

    @app.route('/questions', methods=['GET'])
    @app.route('/questions/<question_id>', methods=['GET', 'POST'])
    def questions(question_id=None):
        if request.method == 'GET':
            try:
                if question_id is not None:
                    only_question_pairs = [preview_pair for preview_pair
                                           in question_preview_pairs
                                           if isinstance(preview_pair[0], Question)
                                           and preview_pair[0].id == int(question_id)]
                else:
                    only_question_pairs = [preview_pair for preview_pair
                                           in question_preview_pairs
                                           if isinstance(preview_pair[0], Question)]

                return render_template("app/generation_results.html",
                                       question_preview_pairs=only_question_pairs)

            except Exception:
                return make_response(jsonify({'error': 'Bad request'}), 400)

        elif request.method == 'POST':
            if question_id is None:
                return make_response(jsonify({'error': 'Bad request'}), 400)

            answer_id = int(request.get_json()["answer_id"])
            question_id = int(question_id)
            if question_id not in handler.question_registry.questions:
                return make_response(jsonify({'error': 'Bad request'}), 400)

            question = handler.question_registry.questions[question_id]
            question.chosen_answer_id = answer_id
            return make_response("OK", 200)

    def generate_preview_single_element(element_id, generate=True):
        try:
            element_id = int(element_id)
            question_preview_pairs.clear()
            if handler.element_generator_table.has_element_by_id(element_id):
                element = data_manipulation.get_element_by_id(element_id)
                for questions, outfolder, preview in handler.generate_single_element(element,
                                                                                    data_manipulation,
                                                                                    "../../files/",
                                                                                    generate):
                    if questions is None or len(questions) == 0:
                        question_preview_pairs.append((None, preview))
                    else:
                        for question in questions:
                            if not handler.question_registry.already_exists(question):
                                handler.question_registry.register_question(question)
                                question_preview_pairs.append((question, preview))

                return render_template("app/generation_results.html", question_preview_pairs=question_preview_pairs)
        except ValueError:
            return make_response(jsonify({'error': 'Bad request'}), 400)

    def generate_preview_all_elements(generate=True):
        try:
            handler.generate_by_diff_generator(data_manipulation, 0, "../../files/", generate)
            return make_response("OK", 200)
        except ValueError:
            return make_response(jsonify({'error': 'Bad request'}), 400)

    return app


def initialize(data_manipulation=None, handler=None, tracer=None):
    for generator in handler.generators.values():
        generator.tracer = tracer
    return data_manipulation, handler, tracer


def remove_temp_files():
    folder = 'templates/temp_diff'
    folder_path = os.path.join(os.getcwd(), folder)
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def main():
    remove_temp_files()
    data_manipulation = DataManipulation()
    data_manipulation = data_manipulation.load_from_json()
    handler = GeneratorHandler().load_from_json()
    tracer = Tracer().load_from_json()
    app = create_app(data_manipulation, handler, tracer)
    app.run(use_reloader=False)


if __name__ == '__main__':
    main()
