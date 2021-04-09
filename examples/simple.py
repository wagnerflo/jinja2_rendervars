from jinja2 import Environment
from jinja2_rendervars import RenderVarsExtension,RenderVar

env = Environment(extensions=[RenderVarsExtension])
var = RenderVar("var", 42)

with env.rendervars() as rvars:
    tmpl = env.from_string("""\
{{ rendervars.var }}
{% rendervar var = 84 -%}
{{ rendervars.var }}
""")
    print(tmpl.render())

print(rvars.var)
print(var)
