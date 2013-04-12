from setuptools import setup


setup(name='Sample Pybtex plugins',
    author='Andrey Golovizin',
    py_modules=['toyplugins'],
    entry_points = {
        'pybtex.database.output': 'python = toyplugins:PythonWriter',
        'pybtex.database.output.suffixes': '.py = toyplugins:PythonWriter',
        'pybtex.database.input': 'python = toyplugins:PythonParser',
        'pybtex.database.input.suffixes': '.py = toyplugins:PythonParser',
    },
)
