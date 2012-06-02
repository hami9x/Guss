import os
import jinja2

jinjaEnv = jinja2.Environment(
        loader = jinja2.FileSystemLoader(os.path.dirname(__file__)))

def render_template(name, values={}):
    return jinjaEnv.get_template(os.path.join("templates", name+".html")).render(values)
