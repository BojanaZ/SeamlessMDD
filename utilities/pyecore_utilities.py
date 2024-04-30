def get_class_from_metamodel(metamodel, class_name):
    for item in metamodel.eClassifiers.items:
        if item.name == class_name:
            return item
