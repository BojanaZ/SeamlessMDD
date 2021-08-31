from GeneratorHandler import GeneratorHandler
from generators.documents_output_generator import DocumentsOutputGenerator
from element_generator_table import ElementGeneratorTable
from DataManipulation import DataManipulation
import json
import dill


def save_generators_json():
    generator_dict = {}
    g1 = DocumentsOutputGenerator()
    g1.id = 1
    #generator_dict[g1.id] = g1
    with open("generators.json", "w") as file:
        file.write(g1.toJSON())

# def load_generators_json():
#     with open("generators.json") as file:
#         generators = file.read()
#         generator_dict = json.loads(generators)

def save_table_dill(table):
    with open("table.dill", "wb") as file:
        dill.dump(table, file)

# def dummy_table():
#     data = GeneratorHandler.dummy_data()
#     generator = DocumentsOutputGenerator()
#     table = ElementGeneratorTable()
#     elements = data.elements
#     for element in elements:
#         table.insert_pair(element, generator)
#     save_table_dill(table)


if __name__ == '__main__':

    handler = GeneratorHandler()
    handler.load_generators_dill()

    data = GeneratorHandler.dummy_data()

    generator = DocumentsOutputGenerator()
    handler.register(generator)
    #dummy_table()
    handler.load_table_dill()
    handler.generate_by_generator(data, "../out/")



