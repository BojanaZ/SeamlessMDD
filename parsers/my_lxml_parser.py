from parsers.parser_interface import IParser
from lxml import html, etree


class MyLXMLParser(IParser):

    def __init__(self, file_path):
        self.tree = html.parse(file_path)

    def get_element_by_id(self, id):
        return self.tree.getroot().get_element_by_id(str(id), None)

    def get_elements_by_name(self, name):
        return self.tree.xpath("//*[@name='%s']" % name)

    def get_element_by_path(self, xpath, **kwargs):
        """
        Finds elements by given xpath
        :param xpath: xpath string with keyword parameters
        :param kwargs: keyword parameters
        :return: found elements, empty list if there is no such elements

        Example:
        xpath = "//{tag_name}[@name='{element_name}']"
        kwargs = {'tag_name': 'div', 'name': 'something'}
        Function returns elements on xpath "//div[@name='something']"
        """
        path = xpath.format(**kwargs)
        return self.tree.xpath(path)

    def element_from_string(self, string):
        return html.fromstring(string)

    def replace_element_by_id(self, id, new_element):
        self.pretty_print(self.tree)
        element_to_replace = self.get_element_by_id(id)
        element_to_replace.addnext(new_element)
        parent = element_to_replace.getparent()
        parent.remove(element_to_replace)

    def pretty_print(self, element_):
        content = etree.tostring(element_, pretty_print=True)
        print(content.decode('UTF-8'))
        print()

    def save_to_file(self, path):
        self.pretty_print(self.tree)
        file = open(path, "w")
        content = etree.tostring(self.tree, pretty_print=True)
        file.write(content.decode('UTF-8'))
        file.close()


if __name__ == '__main__':
    my_parser = MyLXMLParser("sample_files/F1.html")
    element = my_parser.element_from_string("<a>Novi element</a>")
    my_parser.replace_element_by_id(1, element)
    my_parser.save_to_file("sample_files/new_F1.html")
