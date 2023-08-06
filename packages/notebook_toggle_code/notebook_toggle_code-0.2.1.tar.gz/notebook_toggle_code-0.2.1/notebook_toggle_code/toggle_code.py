
import os
import json

import jinja2 as jj

from IPython.display import display, HTML, Markdown


class ToggleCode:
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

    def __init__(self,
                 init_show=True,
                 delay_toggle=0,
                 verbose=False,
                 ):
        """
        """
        self.verbose = verbose
        self.data = {'init_show': init_show,
                     'delay_toggle': delay_toggle
                     }

    def add_js(self):
        """
        """
        template = ToggleCode.env.get_template('main.html')
        html = template.render(data=self.data)

        if self.verbose:
            template = ToggleCode.env.get_template('notice_safe.txt')
            txt = template.render()
            print(txt)

        if self.verbose:
            template = ToggleCode.env.get_template('notice_short.md')
            str_data = json.dumps(self.data)
            md = template.render(str_data=str_data)
            display(Markdown(md))

        display(HTML(html))

    @classmethod
    def info(cls):
        """
        """
        template = ToggleCode.env.get_template('notice_long.md')
        md = template.render()
        display(Markdown(md))
