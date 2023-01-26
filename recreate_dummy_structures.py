#import dill

from metamodel.element_generator_table import ElementGeneratorTable
from transformation.generator_handler import GeneratorHandler
from transformation.generators.documents_output_generator import DocumentsOutputGenerator
from os.path import join
from utilities.utilities import get_project_root
from transformation.data_manipulation import DataManipulation
from tests.dummy_structures import dummy_data


#def save_table_dill(table):
    #with open("table.dill", "wb") as file:
        #dill.dump(table, file)


def dummy_table():
    data = dummy_data()
    generator = DocumentsOutputGenerator()
    generator.initialize()
    table = ElementGeneratorTable()
    elements = data.elements
    for element in elements.values():
        table.insert_pair(element, generator)
    return table


def recreate_dummy_table():
    #TABLE RECREATION FOR FILE
    table = dummy_table()

    path = join(get_project_root(), "files", "table.dill")
    #with open(path, "wb") as file:
        #dill.dump(table, file)

    path = join(get_project_root(), "files", "table.json")
    with open(path, "w") as file:
        file.write(table.to_json())


def recreate_dummy_generator_handler():
    #try:
        #data_manipulation = DataManipulation().load_from_dill()
    #except:
    data_manipulation = recreate_dummy_data_manipulation()

    handler = GeneratorHandler()
    generator = DocumentsOutputGenerator()
    generator.initialize()
    handler.register(generator)

    elements = data_manipulation.get_latest_model().elements
    for element_id, element in elements.items():
        handler.element_generator_table.insert_pair(element, generator)

    #handler.save_to_dill()
    handler.save_to_json()


def recreate_dummy_data_manipulation():
    model = dummy_data()

    data_manipulation = DataManipulation()
    data_manipulation.update_model(model)

    data_manipulation.save_to_json()
    #data_manipulation.save_to_dill()

    return data_manipulation


if __name__ == '__main__':
    dm = recreate_dummy_data_manipulation()
    # recreate_dummy_generator_handler()
    # recreate_dummy_table()
    #
    # print(dm.get_latest_model().get_first_level_dict())





