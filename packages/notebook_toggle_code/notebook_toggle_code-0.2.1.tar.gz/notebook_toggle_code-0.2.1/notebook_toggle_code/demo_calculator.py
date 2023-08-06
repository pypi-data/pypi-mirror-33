
import os
import json

import jinja2 as jj

from IPython.display import display, HTML, Markdown


class DemoCalculator:
    """
    """

    here = os.path.dirname(os.path.abspath(__file__))
    dir_template = os.path.join(here, 'templates')
    loader = jj.FileSystemLoader(dir_template)
    env = jj.Environment(loader=loader,
                         variable_start_string='__$',
                         variable_end_string='$__',
                         block_start_string='{%',
                         block_end_string='%}'
                         )

    def __init__(self):
        """
        """
        template = DemoCalculator.env.get_template('demoCalculator.html')
        html = template.render()
        display(HTML(html))
