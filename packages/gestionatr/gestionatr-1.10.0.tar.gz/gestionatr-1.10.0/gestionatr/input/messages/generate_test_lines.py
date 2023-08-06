# -*- coding: utf-8 -*-
from B70 import Imputacioncostes as ap

atrs = []
while ap.__name__ not in ['object', 'Message', 'MessageBase']:
    atrs += ap.__dict__.keys()
    ap = ap.__base__
out = open("tout.txt", 'w')
txt = "self.assertEqual({0}.{1}, '')\n"
name = 'cons'

xmlatrs = u"""<pcttasacnmc>
<pctcuotagts>
"""

atrsa = sorted([a for a in atrs if a[0] != '_'])
for art in xmlatrs.split():
    if art[1:-1] in atrsa:
        out.write(txt.format(name, art[1:-1]))
