# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['python_ottawa_transit']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'python-ottawa-transit',
    'version': '0.2.0',
    'description': 'Python interface for OCTranspo API',
    'long_description': '# python-ottawa-transit\n\nPython interface to the [OC Transpo](http://www.octranspo.com/developers/documentation) API and utilities for working with the returned data.\n\n## Installation\n\nThe package is available on [PyPi](https://pypi.org/project/python-ottawa-transit)\n```bash\npip install python-ottawa-transit\n```\n\nAlternativly it can be installed from source using [Poetry](https://github.com/sdispater/poetry)\n```bash\ngit clone https://github.com/buckley-w-david/python-ottawa-transit.git\ncd python-ottawa-transit\npoetry install\n```\n\n## Usage\n\n```python3\n>>> from python_ottawa_transit import OCTransportApi\n>>> api = OCTransportApi(app_id = \'APPLICATION_ID\', app_key = \'APPLICATION_KEY\')\n>>> api.get_route_summary_for_stop(stop_no=8435)\n{"GetRouteSummaryForStopResult":{"StopNo":"8435","StopDescription":"BANK \\\\/ COLLINS","Error":"","Routes":{"Route":{"RouteNo":6,"DirectionID":1,"Direction":"Northbound","RouteHeading":"Rockcliffe"}}}}\n```\n',
    'author': 'David Buckley',
    'author_email': 'buckley.w.david@gmail.com',
    'url': 'https://github.com/buckley-w-david/python-ottawa-transit',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
