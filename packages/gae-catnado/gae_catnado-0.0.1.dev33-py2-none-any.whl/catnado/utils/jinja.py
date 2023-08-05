from jinja2 import Environment, FileSystemLoader


def create_jinja_environment(template_path):
  """Get a Jinja environment for rendering a template.

  Args:
    template_path: required str; base location of templates
  """
  return Environment(
    loader=FileSystemLoader(template_path),
  )
