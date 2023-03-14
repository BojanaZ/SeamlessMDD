import difflib
from pathlib import Path
import os
import AdvancedHTMLParser


class Preview(object):
    def __init__(self, previous_version_no, new_version_no, filepath=None, old_view=None, new_view=None):
        self._previous_version = previous_version_no
        self._new_version = new_version_no
        self._filepath = filepath
        self._old_view = old_view
        self._new_view = new_view

    @property
    def previous_version(self):
        return self._previous_version

    @previous_version.setter
    def previous_version(self, previous_version):
        self._previous_version = previous_version

    @property
    def new_version(self):
        return self._new_version

    @new_version.setter
    def new_version(self, new_version):
        self._new_version = new_version

    @property
    def filepath(self):
        return self._filepath

    @filepath.setter
    def filepath(self, filepath):
        self._filepath = filepath

    @property
    def old_view(self):
        return self._old_view

    @old_view.setter
    def old_view(self, old_view):
        self._old_view = old_view

    @property
    def new_view(self):
        return self._new_view

    @new_view.setter
    def new_view(self, new_view):
        self._new_view = new_view

    def generate_diff_view_filename(self):

        return Path(self._filepath).stem + "_" + str(hash(self._old_view)) + "_" + str(hash(self._new_view)) + ".html"

    def generate_diff_view(self):
        f1_content = self._old_view.strip().splitlines()
        if self._new_view:
            f2_content = self._new_view.strip().splitlines()
        else:
            f2_content = []

        diff = difflib.HtmlDiff().make_file(f1_content, f2_content, self.filepath, self.filepath)
        parser = AdvancedHTMLParser.AdvancedHTMLParser()
        parser.parseStr(diff)
        tables = parser.getElementsByXPath("""//body/table""")
        if len(tables) == 0:
            raise Exception("Table tag does not exist")

        table = tables[0]

        filepath_to_return = os.path.join("temp_diff", self.generate_diff_view_filename())
        filepath_to_write = os.path.join("templates", filepath_to_return)
        file = open(filepath_to_write, "w")
        file.writelines(str(table))
        file.close()

        return filepath_to_return


if __name__ == '__main__':
    from parsers.my_html_parser import MyHTMLParser
    parser1 = MyHTMLParser()
    file1 = open("/Users/bojana/Documents/Private/Fakultet/doktorske/DMS-rad/SeamlessMDD/files/Document1.task1.html")
    content1 = file1.read()
    file1.close()

    file2 = open("/Users/bojana/Documents/Private/Fakultet/doktorske/DMS-rad/SeamlessMDD/files/Document2.task1.html")
    content2 = file2.read()
    file2.close()

    preview = Preview(0, 1, "out.html", content1, content2)
    preview.generate_diff_view()

