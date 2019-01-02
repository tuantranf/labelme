from __future__ import print_function

import distutils.spawn
import os.path
import re
from setuptools import find_packages
from setuptools import setup
import shlex
import subprocess
import sys


PY3 = sys.version_info[0] == 3
PY2 = sys.version_info[0] == 2
assert PY3 or PY2


here = os.path.abspath(os.path.dirname(__file__))
version_file = os.path.join(here, 'labelme', '_version.py')
if PY3:
    import importlib
    version = importlib.machinery.SourceFileLoader(
        '_version', version_file
    ).load_module().__version__
else:
    assert PY2
    import imp
    version = imp.load_source('_version', version_file).__version__
del here


install_requires = [
    'lxml',
    'matplotlib',
    'numpy',
    'Pillow>=2.8.0',
    'PyYAML',
    'qtpy',
]

# Find python binding for qt with priority:
# PyQt5 -> PySide2 -> PyQt4,
# and PyQt5 is automatically installed on Python3.
QT_BINDING = None

try:
    import PyQt5  # NOQA
    QT_BINDING = 'pyqt5'
except ImportError:
    pass

if QT_BINDING is None:
    try:
        import PySide2  # NOQA
        QT_BINDING = 'pyside2'
    except ImportError:
        pass

if QT_BINDING is None:
    try:
        import PyQt4  # NOQA
        QT_BINDING = 'pyqt4'
    except ImportError:
        if PY2:
            print(
                'Please install PyQt5, PySide2 or PyQt4 for Python2.\n'
                'Note that PyQt5 can be installed via pip for Python3.',
                file=sys.stderr,
            )
            sys.exit(1)
        assert PY3
        # PyQt5 can be installed via pip for Python3
        install_requires.append('PyQt5')
        QT_BINDING = 'pyqt5'
del QT_BINDING


if sys.argv[1] == 'release':
    if not distutils.spawn.find_executable('twine'):
        print(
            'Please install twine:\n\n\tpip install twine\n',
            file=sys.stderr,
        )
        sys.exit(1)

    commands = [
        'git tag v{:s}'.format(version),
        'git push origin master --tag',
        'python setup.py sdist',
        'twine upload dist/labelme-{:s}.tar.gz'.format(version),
    ]
    for cmd in commands:
        subprocess.check_call(shlex.split(cmd))
    sys.exit(0)


def get_long_description():
    f = open('README.md')

    lines = []
    for line in f:

        def repl(match):
            if not match:
                return

            url = match.group(1)
            if url.startswith('http'):
                return match.group(0)

            url_new = (
                'https://github.com/wkentaro/labelme/blob/master/{}'
                .format(url)
            )
            if re.match(r'.*[\.jpg|\.png]$', url_new):
                url_new += '?raw=true'

            start0, end0 = match.regs[0]
            start, end = match.regs[1]
            start -= start0
            end -= start0

            res = match.group(0)
            res = res[:start] + url_new + res[end:]
            return res

        patterns = [
            r'!\[.*?\]\((.*?)\)',
            r'<img.*?src="(.*?)".*?/>',
            r'\[.*?\]\((.*?)\)',
            r'<a.*?href="(.*?)".*?>',
        ]
        for pattern in patterns:
            line = re.sub(pattern, repl, line)

        lines.append(line)

    f.close()

    return ''.join(lines)


setup(
    name='labelme',
    version=version,
    packages=find_packages(),
    description='Image Polygonal Annotation with Python',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Kentaro Wada',
    author_email='www.kentaro.wada@gmail.com',
    url='https://github.com/wkentaro/labelme',
    install_requires=install_requires,
    license='GPLv3',
    keywords='Image Annotation, Machine Learning',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    package_data={'labelme': ['icons/*', 'config/*.yaml']},
    entry_points={
        'console_scripts': [
            'labelme=labelme.main:main',
            'labelme_draw_json=labelme.cli.draw_json:main',
            'labelme_draw_label_png=labelme.cli.draw_label_png:main',
            'labelme_json_to_dataset=labelme.cli.json_to_dataset:main',
            'labelme_on_docker=labelme.cli.on_docker:main',
        ],
    },
)
