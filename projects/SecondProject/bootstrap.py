from functools import partial
import pyecore.ecore as Ecore
from pyecore.ecore import *
from utilities import utilities
import inspect
from .metamodel.element import Element
from .metamodel.model import Model
from .metamodel.container import Container


name = 'document'
nsURI = 'http://www.example.org/document'
nsPrefix = 'document'

eClass = EPackage(name=name, nsURI=nsURI, nsPrefix=nsPrefix)

eClassifiers = {}
getEClassifier = partial(Ecore.getEClassifier, searchspace=eClassifiers)


def make(modules):
    additional_changes()

    for module_name, module in modules.items():
        my_module_classes = []
        for name, class_ in inspect.getmembers(module, inspect.isclass):
            if class_.__module__ == module_name and hasattr(class_, 'eClass'):
                eClass.eClassifiers.append(class_.eClass)

    return eClass


# Mora naknadno
# Oficijalno objašnjenje, dato u inline komentaru u jednom od primera:
# As the relation is reflexive, it must be set AFTER the metaclass creation
def additional_changes():
    Element.eClass.eStructuralFeatures.append(EReference(name='_model', eType=Model, containment=False))
    Element._model = EReference(name='_model', eType=Model, containment=False)
    Element.eClass.eStructuralFeatures.append(EReference(name='_parent_container',
                                                         eType=Container,
                                                         eOpposite=Container._elements,
                                                         containment=False))

    Element._parent_container = EReference(name='_parent_container',
                                           eType=Container,
                                           eOpposite=Container._elements,
                                           containment=False)


if __name__ == '__main__':
    mm = make()
    print(mm)
