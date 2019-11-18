from metamodel.Container import Container

def create_container():
    return Container(5)


def test_container_creation():
    assert create_container() is not None