from pyjuhelpers.basicconfig import Map, Config, AttrDict

import yaml




data = yaml.load(open(,"r"))

c = Config()
t = AttrDict(data['anycsv'])


data['anycsv']['sniff_lines'] = 30

print(t.sniff_lines)
t.update(data['anycsv'])
print(t.sniff_lines)


print(c.Anycsv.sniff_lines)

c.merge(init=data)
print(c.Anycsv.sniff_lines)

