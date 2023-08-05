# encoding: utf-8
"""
html.py
~~~~~~~

Classes for rendering documents as html.

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-06-06"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports 
import base64
from io import BytesIO

# third party imports
from matplotlib import pyplot as plt

# local imports

# globals


class Report(object):
    """Simple html report class based on bootstrap

    Use the interface to add elements (title, figures, tables, text, etc),
    then use *write* to dump rendered html to file.

    """
    def __init__(self):
        self._components = []
        self._nfig = 0
        self._ntab = 0

    def add_title(self, title, par=None):
        """Add title to document

        :param title: title string
        :param par: paragraph to go with title (optional)
        """
        s = """      <div class="jumbotron">\n        <h1>{}</h1>""".format(title)
        if par: s += """        <p>{}</p>""".format(par)
        s += """      </div>"""
        self._add(s)

    def add_figure(self, cap=""):
        """Add figure to document

        Call this directly after creating a figure with matplotlib.
        The figure will be embedded into the html document.

        :param cap: figure caption (optional)
        """
        self._nfig += 1
        image = BytesIO()
        plt.savefig(image, format='png')
        fig = base64.encodebytes(image.getvalue()).decode()
        htmlfig = """<div align="center">
            <p> <b> Figure {index}:</b> {cap}</p>
            </div> 
            <div class="page-header">
            <img src="data:image/png;base64,{fig}" class="img-thumbnail"/>
            </div>
        """.format(index=self._nfig, cap=cap, fig=fig)
        self._add(htmlfig)

    def add_table(self, tab, cap=""):
        """Add table to document

        :param tab: table (pandas DataFrame)
        :param cap: caption (optional)
        """
        self._ntab += 1
        t = tab.to_html(index=False)
        t = t.replace('<table border="1" class="dataframe">',
                      '<table class="table table-striped">')

        htmltab = """<div align="center">
        <p> <b> Table {index}:</b> {cap}</p>
        </div>
        {tab}""".format(index=self._ntab, cap=cap, tab=t)
        self._add(htmltab)

    def add_styled_table(self, tab, cap=""):
        """Add styled table to document

        Note: full control over html style is given to the Styler and bootstrap css
        is not used, so it can be difficult to get something that actually
        looks good.

        :param tab: table (pandas Styler)
        :param cap: caption (optional)
        """
        self._ntab += 1
        htmltab = """<div align="center">
        <p> <b> Table {index}:</b> {cap}</p>
        </div>
        {tab}""".format(index=self._ntab, cap=cap, tab=tab.render())
        self._add(htmltab)


    def add_section(self, title):
        """Add section to document

        :param title: section title
        """
        html =  """
      <div class="page-header">
        <h2>{}</h2>
      </div>        
        """.format(title)
        self._add(html)

    def add_text(self, text):
        """Add paragraph text to document

        :param text: text string
        """
        html = """<p>{}</p>""".format(text)
        self._add(html)

    def write(self, filename):
        """Write rendered html to file

        :param filename: path to output file
        """
        with open(filename, 'w') as f:
            f.write(self._render())

    def _add(self, text):
        """Add an element to docuemnt (internal function)

        :param text: rendered html text
        """
        self._components.append(text)

    def _render(self):
        """Return complete document in rendered html format (internal function)

        :return: rendered html document (string)
        """
        return '\n'.join([self._header()] + self._components + [self._footer()])

    def _header(self):
        """Return html header

        :return: string
        """
        return """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <meta name="description" content="">
    <meta name="author" content="">

    <title>This is a title</title>

    <!-- Bootstrap core CSS -->
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap theme -->
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" rel="stylesheet">
    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <link href="https://maxcdn.bootstrapcdn.com/css/ie10-viewport-bug-workaround.css" rel="stylesheet">
    <!-- Custom styles for this template -->
    <link href="https://getbootstrap.com/docs/3.3/examples/theme/theme.css" rel="stylesheet">
  </head>

  <body> 
  
  <div class="container theme-showcase" role="main">
        """

    def _footer(self):
        """Return html footer

        :return: string
        """
        return """    </body>\n\n    </html>"""


# EOF