import os
import re

from flask import Flask, request, jsonify, make_response, render_template, redirect, url_for
from transformation.generators.generator_register import GeneratorRegister
from metamodel.model import Model
from transformation.data_manipulation import VersionUnavailableError
from transformation.conflict_resolution.question import Question
from view.tree_view import prepare_model_for_tree_view
from exceptions import ElementNotFoundError
from utilities.utilities import class_object_to_underscore_format, class_name_to_underscore_format, get_os_root
from projects.project_loader import WorkspaceProject
from pyecore_utilities import get_class_from_metamodel


def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config["DEBUG"] = True
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    os.environ['PYTHONPATH'] = os.getcwd()

    initialize()
    question_preview_pairs.clear()

    @app.errorhandler(404)
    def not_found(e):
        return render_template('app/404.html')

    @app.route('/', methods=['GET'])
    @app.route('/home', methods=['GET'])
    def home():
        return redirect(url_for('model'))

    @app.route('/open', methods=['POST'])
    def open():
        if request.method == 'POST':
            import json
            content = request.get_json()
            content = json.loads(content.replace("'", "\""))
            parts = [item for item in re.split(r"\\|\/", content['project_path']) if item != ""]
            project_path = os.path.join(get_os_root(), *parts)
            project_name = content['project_name']
            global project
            project = WorkspaceProject(project_path, project_name)
            initialize()
            project.templates_path = os.path.join(app.root_path, app.template_folder)
            return redirect(url_for('model'))

    @app.route('/models/<version_id>', methods=['GET'])
    def model_by_version(version_id):
        if request.method == 'GET':
            try:
                model = project.data_manipulation.get_model_by_version(version_id)
                content_json = prepare_model_for_tree_view(model)

                latest_version = project.data_manipulation.get_latest_version_number()

                disabled = False
                if version_id != latest_version:
                    disabled = True
                return render_template('model_manipulation/model_tree_view.html', tree_view_model=content_json,
                                       version_id=version_id, disabled=disabled)
            except VersionUnavailableError:
                return make_response(render_template('app/404.html'), 404)

    @app.route('/model', methods=['GET', 'POST'])
    def model():
        if request.method == 'GET':
            try:
                content_json = prepare_model_for_tree_view(project.data_manipulation.get_latest_model())
                version_id = project.data_manipulation.get_latest_version_number()
                return render_template('model_manipulation/model_tree_view.html', tree_view_model=content_json,
                                       version_id=version_id)
            except VersionUnavailableError:
                return make_response(render_template('app/404.html'), 404)
        elif request.method == 'POST':
            """modify/update model"""
            content = request.get_json()
            model_ = Model.from_json(content)
            project.data_manipulation.update_model(model_)
            return make_response("CREATED", 201)

    @app.route('/form-editor/<element_id>/<version_id>', methods=['GET', 'POST'])
    def form_editor(element_id, version_id):
        if request.method == 'GET':
            try:
                element_id = int(element_id)

                has_version = project.data_manipulation.has_version(version_id)
                if not has_version:
                    version_id = project.data_manipulation.get_latest_version_number()
                else:
                    version_id = int(version_id)

                if element_id == -1:
                    element = project.data_manipulation.get_model_by_version(version_id)
                else:
                    element = project.data_manipulation.get_model_by_version(version_id).get_element(element_id)

                disabled = version_id != project.data_manipulation.get_latest_version_number()

                file_name = class_object_to_underscore_format(type(element))

                return render_template('model_manipulation/'+file_name+'.html', element=element, disabled=disabled)
            except ElementNotFoundError:
                return make_response(render_template('app/404.html'), 404)
        elif request.method == 'POST':
            element_id = int(element_id)
            element_dict = request.get_json()
            element = project.data_manipulation.get_latest_model().get_element(element_id)
            element.update(**element_dict)
            return prepare_model_for_tree_view(project.data_manipulation.get_latest_model())

    @app.route('/add-subelement/<parent_id>/<element_type>', methods=['GET', 'POST'])
    def add_element(parent_id, element_type):
        if element_type != 'null':
            module_name = class_name_to_underscore_format(element_type)
            metamodel_class = get_class_from_metamodel(project.data_manipulation.metamodel, element_type)
            element = metamodel_class()

            if request.method == 'GET':
                return render_template('model_manipulation/' + module_name + '.html', element=element,
                                       parent_id=parent_id, element_type=element_type)

            elif request.method == 'POST':
                parent_id = int(parent_id)
                parent_element = project.data_manipulation.get_latest_model().get_element(parent_id)

                element_dict = request.get_json()
                element.id = project.data_manipulation.generate_new_element_id()
                element.update(**element_dict)
                parent_element.add(element)
                return prepare_model_for_tree_view(project.data_manipulation.get_latest_model())

    @app.route('/delete-subelement/<element_id>', methods=['POST'])
    def delete_element(element_id):
        if request.method == 'POST':
            try:
                element_id = int(element_id)
                # If element is model
                if element_id == -1:
                    return make_response("Method Not Allowed", 405)
                else:
                    element = project.data_manipulation.get_latest_model().get_element(element_id)
                    project.data_manipulation.get_latest_model().remove_element(element)
                    return prepare_model_for_tree_view(project.data_manipulation.get_latest_model())
            except ValueError:
                return make_response("Method Not Allowed", 405)
            except ElementNotFoundError:
                return make_response(render_template('app/404.html'), 404)

    @app.route('/save', methods=['POST'])
    def save_model():
        if request.method == 'POST':
            try:
                project.data_manipulation.save_latest_model_to_xmi()
                return make_response("OK", 200)
            except ValueError:
                return make_response("Method Not Allowed", 405)
            except ElementNotFoundError:
                return make_response(render_template('app/404.html'), 404)


    @app.route('/generators', methods=['GET', 'POST'])
    @app.route('/generators/<generator_id>', methods=['GET', 'POST'])
    def generators(generator_id=None):
        if request.method == 'GET':
            try:
                if generator_id:
                    content_json = project.generator_handler.get_generator(int(generator_id)).to_json()
                else:
                    content_json = project.generator_handler.generators.to_json()
                return render_template('app/generator.html', generators=content_json, generator_id=generator_id)
            except KeyError:
                return make_response(render_template('app/404.html'), 404)

        if request.method == 'POST':
            """modify/update generator"""

            content = request.get_json()
            project.generator_handler.generators = GeneratorRegister.from_json(content)
            return make_response("CREATED", 201)

    @app.route('/table', methods=['GET', 'POST'])
    def element_generator_table():
        if request.method == 'GET':
            try:
                content = project.generator_handler.element_generator_table.to_json()
                return render_template('app/element_generator_table.html', table=content)
            except Exception as e:
                return make_response(render_template('app/404.html'), 404)

        elif request.method == 'POST':
            try:
                content = request.get_json()
                project.generator_handler.element_generator_table.register_from_json(content)
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

    @app.route('/generate/all', methods=['GET'])
    def generate_all_elements():
        generate_preview_all_elements(True)
        return redirect(url_for('get_generation_results'))

    @app.route('/generate/<element_id>', methods=['GET'])
    def generate_single_element(element_id):
        #try:
        generate_preview_single_element(element_id, True)
        return redirect(url_for('get_generation_results'))
        #except ValueError:
        #    return make_response(jsonify({'error': 'Bad request'}), 400)

    @app.route('/generate-by-generator/<generator_id>', methods=['GET'])
    def generate_by_generator(generator_id):
        try:
            generate_preview_by_generator(generator_id, True)
            return redirect(url_for('get_generation_results'))
        except ValueError:
            return make_response(jsonify({'error': 'Bad request'}), 400)

    @app.route('/preview/all', methods=['GET'])
    def preview_all_elements():
        generate_preview_all_elements(False)
        return redirect(url_for('get_generation_results'))

    @app.route('/preview/<element_id>', methods=['GET'])
    def preview_single_element(element_id):
        generate_preview_single_element(element_id, False)
        return redirect(url_for('get_generation_results'))

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
            if question_id not in project.generator_handler.question_registry.questions:
                return make_response(jsonify({'error': 'Bad request'}), 400)

            question = project.generator_handler.question_registry.questions[question_id]
            question.chosen_answer_id = answer_id
            return make_response("OK", 200)

    def generate_preview_single_element(element_id, generate=True):
        element_id = int(element_id)
        question_preview_pairs.clear()
        if project.generator_handler.element_generator_table.has_element_by_id(element_id):
            element = project.data_manipulation.get_element_by_id(element_id)
            for questions, outfolder, preview in project.generator_handler.generate_single_element(element,
                                                                                         project.data_manipulation,
                                                                                         "../../files/",
                                                                                         generate):
                if questions is None or len(questions) == 0:
                    question_preview_pairs.append((None, preview))
                else:
                    for question in questions:
                        if not project.generator_handler.question_registry.already_exists(question):
                            project.generator_handler.question_registry.register_question(question)
                            question_preview_pairs.append((question, preview))

    def generate_preview_by_generator(generator_id, generate=True):
        generator_id = int(generator_id)
        question_preview_pairs.clear()
        if project.generator_handler.element_generator_table.has_generator_by_id(generator_id):
            for questions, outfolder, preview in project.generator_handler.generate_single_generator(project.data_manipulation,
                                                                                           generator_id,
                                                                                           "../../files/",
                                                                                           generate):
                if questions is None or len(questions) == 0:
                    question_preview_pairs.append((None, preview))
                else:
                    for question in questions:
                        if not project.generator_handler.question_registry.already_exists(question):
                            project.generator_handler.question_registry.register_question(question)
                            question_preview_pairs.append((question, preview))

    def generate_preview_all_elements(generate=True):
        question_preview_pairs.clear()
        for questions, outfolder, preview in project.generator_handler.generate_all_generators(project.data_manipulation,
                                                                                     "files",
                                                                                     generate):
            if questions is None or len(questions) == 0:
                question_preview_pairs.append((None, preview))
            else:
                for question in questions:
                    if not project.generator_handler.question_registry.already_exists(question):
                        project.generator_handler.question_registry.register_question(question)
                        question_preview_pairs.append((question, preview))

    return app


def initialize():
    for generator in project.generator_handler.generators.values():
        generator.tracer = project.tracer


def main():
    project_package = "/Users/bojana/Documents/Private/Fakultet/doktorske/DMS-rad/SeamlessMDD/projects/FirstProject"
    global project
    project = WorkspaceProject(project_package, "FirstProject")
    app = create_app()
    project.templates_path = os.path.join(app.root_path, app.template_folder)

    app.run(use_reloader=False)


if __name__ == '__main__':
    project = None
    question_preview_pairs = []
    main()
