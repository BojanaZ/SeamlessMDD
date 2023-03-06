from flask import Flask, request, jsonify, make_response


def extend(app, data_manipulation_, handler_, tracer_):

    @app.route('/additional', methods=['GET', 'POST'])
    def additional():
        try:
            gen_obj = handler_.generate_by_diff_generator(data_manipulation_, 0, "../files/")
            for obj in gen_obj:
                return make_response(jsonify(obj), 200)
            return make_response("OK", 200)
        except ValueError:
            return make_response(jsonify({'error': 'Bad request'}), 400)

    return app
