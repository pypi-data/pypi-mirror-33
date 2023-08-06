#coding=utf-8
'''
Created on Jul 2, 2012

@author: davyzhang
'''
from message_pb2 import CityAoi, CityAois
from dict_to_protobuf import dict_to_protobuf, protobuf_to_dict


def test_parse_dict():
    obj = {'player':[{'role_id':1,'target_x':23},{'role_id':2,'target_x':24}]}
    proto_obj = CityAoi()
    dict_to_protobuf(obj, proto_obj)
    assert (proto_obj.player[0].role_id ==  1)
    assert (proto_obj.player[1].target_x == 24)

    obj2 = protobuf_to_dict(proto_obj)
    print (obj2)
    print (obj)


def test_parse_dict_call_backwards():
    obj = {'player':[{'role_id':1,'target_x':23},{'role_id':2,'target_x':24}]}
    proto_obj = CityAoi()
    dict_to_protobuf(proto_obj,obj)
    assert (proto_obj.player[0].role_id == 1)
    assert (proto_obj.player[1].target_x == 24)

    obj2 = protobuf_to_dict(proto_obj)
    print (obj2)
    print (obj)


def test_parse_list():
    obj = [{'player': [{'role_id': 1, 'target_x': 23}, {'role_id': 2, 'target_x': 24}]}]
    proto_obj = CityAois()
    dict_to_protobuf(obj, proto_obj)
    assert proto_obj.CAS[0].player[0].role_id == 1
    assert proto_obj.CAS[0].player[1].target_x == 24
    obj2 = protobuf_to_dict(proto_obj)
    print (obj2)
    print (obj)

if __name__ == "__main__":
    test_parse_dict()
    test_parse_dict_call_backwards()
    test_parse_list()
