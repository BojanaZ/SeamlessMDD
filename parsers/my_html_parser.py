from parsers.parser_interface import IParser
import AdvancedHTMLParser


class MyHTMLParser(IParser):

    def __init__(self, file_path):
        self.parser = AdvancedHTMLParser.AdvancedHTMLParser(file_path, encoding='utf-8')

    def get_element_by_id(self, id_):
        return self.parser.getElementById(str(id_))

    def get_element_by_name(self, name):
        elements = self.parser.getElementsByAttr("name", name)
        if len(elements) == 0:
            return None
        return elements[0]

    def get_element_by_path(self, path):
        raise NotImplementedError


if __name__ == '__main__':
    my_parser = MyHTMLParser("sample_files/F1.html")
    print(my_parser.get_element_by_name("nesto"))
