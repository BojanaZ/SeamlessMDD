from metamodel.model import Model
from metamodel.project import Project
from metamodel.document import Document
from metamodel.field import Field

def dummy_data():

    model = Model()

    project = Project(1, "MyProject", False, None, model)

    model.root = project

    document1 = Document(11, "Document1", False, None, model)
    document2 = Document(12, "Document2", False, None, model)
    project.add(document1)
    project.add(document2)

    field1 = Field(89, "Fifi1", False, None, model)
    field2 = Field(90, "Fifi2", False, None, model)
    field3 = Field(91, "Fifi3", False, None, model)
    field4 = Field(92, "Fifi4", False, None, model)
    field5 = Field(93, "Fifi5", False, None, model)

    document1.add(field1)
    document1.add(field2)
    document1.add(field3)
    document2.add(field4)
    document2.add(field5)

    return model