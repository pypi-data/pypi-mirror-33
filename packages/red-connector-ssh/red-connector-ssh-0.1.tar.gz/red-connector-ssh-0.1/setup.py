# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['red_connector_ssh']

package_data = \
{'': ['*']}

install_requires = \
['jsonschema>=2.6,<3.0', 'paramiko>=2.4,<3.0']

setup_kwargs = {
    'name': 'red-connector-ssh',
    'version': '0.1',
    'description': 'RED Connector SSH is part of the Curious Containers project.',
    'long_description': '# RED Connector SSH\n\nRED Connector SSH is part of the Curious Containers project.\n\nFor more information please refer to the Curious Containers [documentation](https://curious-containers.github.io/).\n\n## Acknowledgements\n\nThe Curious Containers software is developed at [CBMI](https://cbmi.htw-berlin.de/) (HTW Berlin - University of Applied Sciences). The work is supported by the German Federal Ministry of Economic Affairs and Energy (ZIM project BeCRF, grant number KF3470401BZ4), the German Federal Ministry of Education and Research (project deep.TEACHING, grant number 01IS17056) and HTW Berlin Booster.\n\n',
    'author': 'Christoph Jansen',
    'author_email': 'Christoph.Jansen@htw-berlin.de',
    'url': 'https://curious-containers.github.io/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
