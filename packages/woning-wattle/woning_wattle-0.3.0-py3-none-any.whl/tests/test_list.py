from wattle import List, String, load_schema


def test_list():
    class Schema:
        mylist = List(String())

    schema = load_schema(Schema)
    obj = schema.read_dict({'mylist': ['a', 'b', 'c']})
    assert isinstance(obj.mylist, list)
    assert obj.mylist == ['a', 'b', 'c']


def test_list_nested():
    class MyObj:
        name = String()
        value = String()

    class Schema:
        mylist = List(MyObj)

    schema = load_schema(Schema)
    obj = schema.read_dict({'mylist': [
        {'name': 'test1', 'value': 'test1'},
        {'name': 'test2', 'value': 'test2'},
        {'name': 'test3', 'value': 'test3'},
    ]})
    assert len(obj.mylist) == 3
    assert all(isinstance(o, MyObj) for o in obj.mylist)
    assert obj.mylist[0].name == 'test1'
    assert obj.mylist[0].value == 'test1'
    assert obj.mylist[1].name == 'test2'
    assert obj.mylist[1].value == 'test2'
    assert obj.mylist[2].name == 'test3'
    assert obj.mylist[2].value == 'test3'
