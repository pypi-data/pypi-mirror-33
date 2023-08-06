
from mlshed import Model


test_model1 = Model(
    name='test1',
    task='testing',
)


def test_fname():
    some_name = test_model1.fname()
    assert some_name.endswith('.pkl')
    tag1 = 'hovercraft'
    name_with_tag = test_model1.fname(tags=[tag1])
    assert name_with_tag.endswith('.pkl')
    assert tag1 in name_with_tag
