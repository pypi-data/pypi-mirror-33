from defs import SUBTYPES_R101
model_str = """<record model="giscedata.subtipus.reclamacio" id="sw_subtipus_reclamacio_{0}">
    <field name="code">{0}</field>
    <field name="name">{1}</field>
    <field name="type">{2}</field>
</record>
"""
with open("subtipus_data.xml", "w") as f:
    for elem in SUBTYPES_R101:
        f.write(model_str.format(elem['code'], elem['name'], elem['type']))
