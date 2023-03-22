from parsers.parser_interface import IParser
import AdvancedHTMLParser
from utilities.exceptions import ParsingError


class MyHTMLParser(IParser):

    def __init__(self, file_path=None):
        self.parser = AdvancedHTMLParser.AdvancedHTMLParser(file_path, encoding='utf-8')

    def get_element_by_id(self, id_):
        return self.parser.getElementById(str(id_))

    def check_if_element_exists(self, id_):
        try:
            element = self.get_element_by_id(id_)
            if element:
                return True, element
        except:
            pass
        return False, None

    def get_element_by_name(self, name):
        elements = self.parser.getElementsByAttr("name", name)
        if len(elements) == 0:
            return None
        return elements[0]

    def get_element_by_path(self, path):
        raise NotImplementedError

    def get_elements_by_value(self, value):
        nodes = self.parser.getAllNodes()
        result_nodes = []
        for node in nodes:
            if value in node.innerText:
                result_nodes.append(node)

        return result_nodes

    def replace_element_by_id(self, id_, new_element):
        element = self.get_element_by_id(id_)
        self.update_node(element, new_element)

    def remove_element_by_id(self, id_):
        element = self.get_element_by_id(id_)
        element.parentNode.removeNode(element)

    def get_elements_by_jinja_variable(self, variable_name):
        nodes = self.parser.getAllNodes()
        result_nodes = set()

        for node in nodes:
            if "{{" in node.innerText and "}}" in node.innerText:
                if variable_name in node.innerText:
                    result_nodes.add(node)

            elif "{%" in node.innerText and "%}" in node.innerText:
                if variable_name in node.innerText:
                    result_nodes.add(node)

            elif node.parentNode in result_nodes:
                result_nodes.add(node)

            for attribute_name, attribute_value in node.attributes.items():
                if variable_name.strip() == attribute_value.replace("{{", "").replace("}}", "").strip():
                    result_nodes.add(node)

        return result_nodes

    @classmethod
    def get_element_xpath(cls, element):
        xpath = element.nodeName
        while element.parentNode is not None:
            element = element.parentNode
            xpath = element.nodeName + "/" + xpath

        return "/" + xpath

    def update_element_by_id(self, id_, attribute_name, new_value, important_data=None):
        elements = self.get_element_by_id(str(id_))
        for element in elements:
            element.attributes[attribute_name] = new_value

    def update_element(self, old_element, new_element_text, important_data=None):
        new_parser = MyHTMLParser()
        new_parser.parser.parseStr(new_element_text)
        #error handling
        self.update_node(old_element, new_parser.parser.root, important_data)

    # def update_element_by_path(self, old_element_path, new_element_content, important_data=None):
    #     # index = new_element_path.rindex("/")
    #     # new_element_text = new_element_path[index+1:]
    #     # new_element_path = new_element_path[:index]
    #     # parent_xpath = self.get_element_xpath(old_element.parentNode)
    #     # if parent_xpath != new_element_path:
    #     #     raise Exception("Old element xpath does not match the new one.")
    #
    #     old_element = self.get_elements_by_path(old_element_path)
    #     if len(old_element) != 1:
    #         return
    #     old_element = old_element[0]
    #     self.merge_nodes(old_element, new_element_content, important_data)

    def update_element_by_path(self, old_element_path, new_element_path, new_element_content, important_data=None):
        old_element = self.get_elements_by_path(old_element_path)
        if len(old_element) != 1:
            raise ParsingError("Xpath " + new_element_path + "does not selects single node.")
        old_element = old_element[0]

        new_parser = MyHTMLParser()
        new_parser.parser.parseStr(new_element_content)
        new_element = new_parser.parser.getElementsByXPath(new_element_path)
        if len(new_element) != 1:
            raise ParsingError("Xpath " + new_element_path + "does not selects single node.")
        new_element = new_element[0]
        self.update_node(old_element, new_element, important_data)

    def merge_nodes(self, first_subtree, second_subtree, important_data=None):
        self.update_node(first_subtree, second_subtree, important_data)
        if len(first_subtree.children) == 0:
            for second_child in second_subtree.children:
                first_subtree.appendChild(second_child)
        else:
            for second_child in second_subtree.children:
                for first_child in first_subtree.children:
                    if second_child.nodeName == first_child.nodeName:
                        if ('_id' in second_child.attributes and
                            second_child.attributes['_id'] == first_child.attributes['_id']) or \
                                second_child.innerText == first_child.innerText:
                            self.merge_nodes(first_child, second_child, important_data)
                            break
                else:
                    first_subtree.appendChild(second_child)

    @classmethod
    def update_node(cls, first_node, second_node, important_data=None):
        if hasattr(second_node, "attributes"):
            for second_attr in second_node.attributes:
                if important_data is None or second_attr in important_data:
                    #insert attribute with value from second_node
                    if not hasattr(first_node, "attributes"):
                        first_node.attributes = {}

                    first_node.attributes[second_attr] = second_node.attributes[second_attr]

        if important_data is None or 'text' in important_data:
            first_node.removeText(first_node.text)
            first_node.appendText(second_node.text)

    @classmethod
    def equals(cls, node1, node2):
        if node1.nodeName == node2.nodeName:
            if node1.attributes['_id'] == node2.attributes['_id']:
                return True
        return False

    def get_xpath_for_element(self, element):

        path = element.nodeName
        text = " ".join(element.innerText.split())
        if text:
            path += "[ text() = '" + element.innerText + "' ]"

        if "_id" in element.attributes:
            path += "[ @_id = '" + element.attributes["_id"] + "' ]"

        current_element = element
        while current_element.parentElement is not None:
            current_element = current_element.parentElement
            relative_element_path = current_element.nodeName
            if '_id' in current_element.attributes and not self.is_jinja_variable(current_element.attributes["_id"]):
                relative_element_path += "[ @_id = " + current_element.attributes["_id"] + " ]"

            path = relative_element_path + "/" + path

        return "/" + path

    def get_template_html_from_xpath(self, element, template_path):

        xpath = self.get_xpath_for_element(element)

        template_parser = AdvancedHTMLParser.AdvancedHTMLParser(template_path)
        node = template_parser.getElementsByXPathExpression(xpath)
        if len(node) == 0:
            raise Exception("No such an element")
        elif len(node) > 1:
            raise Exception("Undecisive xpath. Cannot select only one node.")
        return node[0].outerHTML

    @classmethod
    def is_jinja_variable(cls, value):
        if "{{" in value or "}}" in value:
            return True

        return False

    def get_elements_by_path(self, path):
        return self.parser.getElementsByXPath(path)

    def delete_elements_by_path(self, path):
        elements = self.parser.getElementsByXPath(path)
        for element in elements:
            element.remove()

    def wrap_element(self, element, wrapper_tag, classes=None):
        new_parser = MyHTMLParser()
        new_parser.parser.parseStr(wrapper_tag)
        new_node = new_parser.parser.root
        for class_ in classes:
            new_node.addClass(class_)

        element.parentNode.insertBefore(new_node, element)
        element.parentNode.removeChild(element)
        new_node.appendChild(element)

    def replace_content(self, path, new_content):
        elements = self.parser.getElementsByXPath(path)

        new_parser = MyHTMLParser()
        new_parser.parser.parseStr(new_content)
        new_node = new_parser.parser.root

        path = self.simplify_xpath(path)

        if len(elements) > 1:
            return

        if len(elements) == 0:
            self.insert_element_by_path(path, new_content)
        else:
            old_node = elements[0]
            parent = old_node.parentNode
            parent.insertAfter(new_node, old_node)
            parent.removeNode(old_node)

    def find_adequate_node_for_insert(self, path, missing_nodes=None, last_tag=None, latest_tag=None):

        elements = self.parser.getElementsByXPath(path)
        if len(elements) == 0:
            last_part_start = path.rindex('/') + 1
            try:
                last_part_tag_end = path.rindex('[')
            except:
                last_part_tag_end = len(path)

            latest_tag_name = path[last_part_start:last_part_tag_end]
            latest_tag = AdvancedHTMLParser.AdvancedTag(latest_tag_name)
            if last_tag is None:
                last_tag = latest_tag
            else:
                if missing_nodes is None:
                    missing_nodes = latest_tag
                else:
                    latest_tag.appendChild(missing_nodes)
            path = path[0:last_part_start-1]
            return self.find_adequate_node_for_insert(path, missing_nodes, last_tag, latest_tag)
        else:
            if last_tag != latest_tag:
                return last_tag, elements[-1], missing_nodes, latest_tag
            return last_tag, elements[-1], missing_nodes, None

    def simplify_xpath(self, xpath):
        xpath_beginning = xpath
        try:
            last_open_bracket = xpath.rindex('[')
        except ValueError:
            return xpath
        last_close_bracket = xpath.rindex(']')
        brackets_content = xpath[last_open_bracket+1:last_close_bracket]
        attr, new_value = brackets_content.split('=')
        if attr.strip() == 'text()':
            new_value = new_value.replace("\'", "")
            new_value = new_value.replace("\"", "")
            if new_value.strip() == '':
                xpath = xpath[:last_open_bracket]

        if xpath_beginning != xpath:
            return self.simplify_xpath(xpath)
        return xpath

    def check_if_node_exists(self, xpath, node):
        node_tag = node.tagName

        last_part_start = xpath.rindex('/')
        xpath = xpath[:last_part_start]

        xpath += "/" + node_tag
        if '_id' in node.attributes:
            xpath += "[@_id = '" + node.attributes['_id'] + "' ]"
        if node.innerText.strip() != "":
            xpath += "[text() = '" + node.innerText + "' ]"
        try:
            elements = self.parser.getElementsByXPath(xpath)
            return elements is not None and len(elements) != 0
        except:
            return False

    def insert_element_by_path(self, path, element_text):
        self._insert_element_by_path(path, element_text)

    def _insert_element_by_path(self, path, element_text, after_node=None):

        new_parser = MyHTMLParser()
        new_parser.parser.parseStr(element_text)
        new_node = new_parser.parser.root

        path = self.simplify_xpath(path)
        elements = self.parser.getElementsByXPath(path)

        if len(elements) > 1:
            return

        if len(elements) == 0:
            after_node, parent, missing_nodes, latest_node = self.find_adequate_node_for_insert(path)
            if self.check_if_node_exists(path, new_node):
                return
            if latest_node is None:
                parent.appendChild(new_node)
            else:
                parent.appendChild(missing_nodes)
                latest_node.appendChild(new_node)
        else:
            parent = elements[0]

            if self.check_if_node_exists(path, new_node):
                self.merge_nodes(parent, new_node)
                return
                # if len(new_node.children) == 0:
                #     return
                # else:
                #     for child in new_node.children:
                #         new_path = path + "/" + new_node.tagName + "[ text() = '" + new_node.innerText + "'"
                #         if not self.check_if_node_exists(new_path, child):

            if after_node is None:
                parent.appendChild(new_node)
            else:
                parent.insertAfter(new_node, after_node)

    def __str__(self):
        return self.parser.toHTML()

    def write_to_file(self, file_path):
        import os
        print(os.path.abspath(file_path))
        with open(file_path, "w") as file:
            file.write(str(self))


if __name__ == '__main__':
    my_parser = MyHTMLParser("sample_files/F1.html")
    print(my_parser.get_element_by_name("nesto"))
