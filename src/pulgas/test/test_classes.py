import unittest

import attr
import schema
import toml

import pulgas

@pulgas.config()
class Pipfile(object):

    @pulgas.config()
    class Source(object):

        url = pulgas.attrib(schema=str)
        verify_ssl = pulgas.attrib(schema=schema.Optional(bool))
        name = pulgas.attrib(schema=str)

    ## Copied from PEP 508, removed "extra"
    @pulgas.config()
    class Requires(object):

        os_name = pulgas.attrib(schema=schema.Optional(str))
        sys_platform = pulgas.attrib(schema=schema.Optional(str))
        platform_machine = pulgas.attrib(schema=schema.Optional(str))
        platform_python_implementation = pulgas.attrib(schema=schema.Optional(str))
        platform_release = pulgas.attrib(schema=schema.Optional(str))
        platform_system = pulgas.attrib(schema=schema.Optional(str))
        platform_version = pulgas.attrib(schema=schema.Optional(str))
        python_version = pulgas.attrib(schema=schema.Optional(str))
        python_full_version = pulgas.attrib(schema=schema.Optional(str))
        implementation_name = pulgas.attrib(schema=schema.Optional(str))
        implementation_version = pulgas.attrib(schema=schema.Optional(str))

    @pulgas.config()
    class Packages(object):

        packages = pulgas.attrib(default=attr.Factory(dict))

        @classmethod
        def __pulgas_from_config__(cls, config):
            my_schema = schema.Schema({str:
                                       schema.Or(str, # Should be version str
                                                 pulgas.Use(PackageSpec))})
            validated_config = my_schema.validate(config)
            packages = {name: PackageSpec(version=value)
                              if isinstance(value, str)
                              else value}
            return cls(packages=packages)

    source = pulgas.attrib(schema=[pulgas.Use(Source)],
                           default=Source(url='https://pypi.python.org/simple',
                                          verify_ssl=True,
                                          name='pypi'))

    requires = pulgas.attrib(schema=schema.Optional(pulgas.Use(Requires)))

    packages = pulgas.attrib(schema=schema.Optional(pulgas.Use(Packages)))

    dev_packages = pulgas.attrib(schema=schema.Optional(pulgas.Use(Packages)))

class ClassTest(unittest.TestCase):

    def test_simple_pipfile(self):
        content = """
        [[source]]
        url = 'https://pypi.python.org/simple'
        verify_ssl = true
        name = 'pypi'

        [requires]
        python_version = '2.7'

        [packages]
        requests = { extras = ['socks'] }
        records = '>0.5.0'
        django = { git = 'https://github.com/django/django.git', ref = '1.11.4', editable = true }
        "e682b37" = {file = "https://github.com/divio/django-cms/archive/release/3.4.x.zip"}
        "e1839a8" = {path = ".", editable = true}
        pywinusb = { version = "*", os_name = "=='nt'", index="pypi"}

        [dev-packages]
        nose = '*'
        unittest2 = {version = ">=1.0,<3.0", markers="python_version < '2.7.9' or (python_version >= '3.0' and python_version < '3.4')"}
        """
        lines = content.splitlines()[1:]
        initial_whitespace = len(lines[0]) - len(lines[0].lstrip())
        stripped = [line[initial_whitespace:] for line in lines]
        real_content = '\n'.join(stripped) + '\n'
        parsed = toml.loads(real_content)
        res = Pipfile.validate(parsed)
        raise ValueError(res)
