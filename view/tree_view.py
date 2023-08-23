import json


def transform(model_element):
    return model_element.convert_to_tree_view_dict()


def prepare_model_for_tree_view(model):
    model_dict = model.convert_to_tree_view_dict()
    return json.dumps({"core": {"data": [model_dict]},
                       "types": {
                           "Model": {"valid_children": ["Project"]},
                           "Project": {"valid_children": ["Document"]},
                           "Document": {"valid_children": ["Field", "TypedField"]},
                           "Field": {},
                           "TypedField": {}
                       },
                       "plugins": ["types"]
                       })
