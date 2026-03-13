from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_email(template_name: Optional[str], context: Optional[dict], body_html: Optional[str]) -> str:
    if body_html:
        return body_html

    if not template_name:
        raise ValueError("Se requiere template_name o body_html.")

    template = jinja_env.get_template(template_name)
    return template.render(**(context or {}))