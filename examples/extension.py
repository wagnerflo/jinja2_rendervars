from jinja2 import Environment
from jinja2.ext import Extension
from jinja2.nodes import CallBlock,Const
from jinja2_rendervars import RenderVarsExtension,RenderVar

class MetadataExtension(Extension):
    tags = frozenset(["metadata"])

    @RenderVar("metadata")
    def metadata():
        return {
            'this': 42,
            'that': 84,
        }

    def parse(self, parser):
        next(parser.stream)
        token = parser.stream.expect("integer")
        return CallBlock(
            self.call_method(
                "_mul",
                [ Const(token.value, lineno=token.lineno) ],
                lineno=token.lineno
            ),
            [], [], [],
            lineno=token.lineno
        )

    def _mul(self, mul, caller):
        for key in self.metadata:
            self.metadata[key] *= mul
        return ""


env = Environment(extensions=[
    RenderVarsExtension,
    MetadataExtension,
])

with env.rendervars() as rvars:
    env.from_string("{% metadata 2 %}").render()

print(rvars)
print(MetadataExtension.metadata)
