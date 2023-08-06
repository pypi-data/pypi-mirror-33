from pyjuhelpers.basicconfig import  Config, AttrDict

import yaml


def test_dot_access():
    c = Config("configa.yaml")
    assert c.anycsv is not None
    assert c.anyCSV is not None

    assert c.anycsv.sniff_lines == 50
    assert c.anyCSV.sniff_lines == 50

def test_updates():
    c = Config("configa.yaml")

    assert c.anycsv.sniff_lines == 50

    c.merge("configb.yaml")
    assert c.anycsv.sniff_lines == 30