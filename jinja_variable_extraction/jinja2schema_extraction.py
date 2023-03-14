from jinja2schema import infer
from jinja2schema.model import Dictionary, Scalar
from jinja2 import Template
import os
from parsers.my_html_parser import MyHTMLParser


def extract_variables_from_path(path_, template_name_=None, **kwargs):
    # environment = jinja2.Environment(
    #     loader=jinja2.FileSystemLoader(path),
    #     **kwargs
    # )
    #
    # template = environment.get_template(template_name)
    if template_name_ is not None:
        path_ = os.path.join(path_, template_name_)

    with open(path_) as file:
        template = file.read()

    # context = self.create_template_context(element=element)
    s = infer(template)
    return s


def create_lookup_strings(variable_dict, leaf=True, prefix="", variable_names_list=None):
    if variable_names_list is None:
        variable_names_list = set()

    for key, value in variable_dict.items():
        current_variable_name = key

        if prefix is not "":
            current_variable_name = prefix + "." + current_variable_name

        if not leaf or type(value) == Scalar:
            variable_names_list.add(current_variable_name)

        if type(value) is Dictionary:
            variable_names_list.update(create_lookup_strings(variable_dict[key],
                                                             leaf,
                                                             current_variable_name,
                                                             variable_names_list))

    return list(variable_names_list)


def print_mapping(mapping):
    for jinja_variable, paths in mapping.items():
        print(jinja_variable + ": ")
        for path in paths:
            print(" "*30 + path)


def relevant_jinja_variables(diff, template_path, template_name_=None):

    xpaths = extract_elements_from_template(template_path, template_name_)
    old_element = diff.old_object_ref
    new_element = diff.new_object_ref
    property_name = diff.property_name

    jinja_variable_names_start = "element." + property_name

    relevant_paths = []

    for variable, paths in xpaths.items():
        if variable.startswith(jinja_variable_names_start):
            for path_ in paths:
                # select path in old file - if it does not exist - ERROR, question
                #                         - if exists, parser.get_elements_by_path(..)
                #                               change element value
                # obj = object()
                # obj.__class__[property_name] = diff.new_value

                old_path = Template(path_).render(element=old_element)
                new_path = Template(path_).render(element=new_element)
                relevant_paths.append({"old_path": old_path, "new_path": new_path})
    return relevant_paths


def relevant_jinja_variables2(diff, template_path, template_name_=None, leaf=True):

    mapping = extract_elements_from_template(template_path, template_name_, leaf)
    old_element = diff.old_object_ref
    new_element = diff.new_object_ref
    property_name = diff.property_name

    jinja_variable_names_start = "element"
    if property_name not in ["", None]:
        jinja_variable_names_start += "." + property_name

    relevant_paths = []

    for variable, paths_and_elements in mapping.items():
        if variable.startswith(jinja_variable_names_start):
            for path in paths_and_elements:
                # select path in old file - if it does not exist - ERROR, question
                #                         - if exists, parser.get_elements_by_path(..)
                #                               change element value
                # obj = object()
                # obj.__class__[property_name] = diff.new_value
                old_element_xpath = path['xpath']
                new_element_template_path = path['path']

                if old_element is not None:
                    old_path = Template(old_element_xpath).render(element=old_element)
                else:
                    old_path = old_element_xpath

                if new_element is not None:
                    new_path = Template(new_element_template_path).render(element=new_element)
                else:
                    new_path = new_element_template_path

                relevant_paths.append({"old_path": old_path, "new_path": new_path, "new_element": new_element})
    return relevant_paths


def extract_xpaths_from_template(template_path, template_name_):
    path_ = os.path.join(template_path, template_name_)
    variable_dict = extract_variables_from_path(template_path, template_name_)
    # print(variable_dict)
    parser = MyHTMLParser(path_)

    variable_xpath_mapping = {}

    lookup_strings = create_lookup_strings(variable_dict)
    for variable_name in lookup_strings:
        variable_xpath_mapping[variable_name] = []
        elements = parser.get_elements_by_jinja_variable(variable_name)
        for element in elements:
            variable_xpath_mapping[variable_name].append(parser.get_template_html_from_xpath(element, path_))

    return variable_xpath_mapping
    # elements = parser.get_elements_by_value(jinja_variable_name)
    # xpath = parser.get_path_for_element(elements[0])
    # print(xpath)
    #
    # element = parser.get_elements_by_path(xpath)
    # print(element)

    # results = parser.get_elements_by_jinja_variable(jinja_variable_name)
    # print([str(result) for result in results])


def extract_elements_from_template(template_path, template_name_, leaf=True):
    path_ = os.path.join(template_path, template_name_)
    variable_dict = extract_variables_from_path(template_path, template_name_)
    parser = MyHTMLParser(path_)

    variable_element_mapping = {}

    lookup_strings = create_lookup_strings(variable_dict, leaf)
    for variable_name in lookup_strings:
        variable_element_mapping[variable_name] = []
        elements = parser.get_elements_by_jinja_variable(variable_name)
        for element in elements:
            data_dict = {'element': element,
                         'xpath': parser.get_xpath_for_element(element),
                         'path': parser.get_template_html_from_xpath(element, path_)
                        }

            variable_element_mapping[variable_name].append(data_dict)

    return variable_element_mapping


if __name__ == '__main__':
    path = "../generator_templates/"
    template_name = "first_template.tpl"
    # list = create_lookup_strings(extract_variables_from_path(path, template_name))
    # print(list)

    extract_xpaths_from_template(path, template_name)
