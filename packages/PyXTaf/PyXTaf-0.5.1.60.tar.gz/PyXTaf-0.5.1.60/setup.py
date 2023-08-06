#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'PyXTaf',
        version = '0.5.1.0',
        description = 'Extensible Test Automation Framework',
        long_description = '\nExtensible Test Automation Framework\n',
        author = '',
        author_email = '',
        license = '',
        url = '',
        scripts = [],
        packages = [
            'taf',
            'taf.foundation',
            'taf.modeling',
            'taf.foundation.conf',
            'taf.foundation.api',
            'taf.foundation.plugins',
            'taf.foundation.utils',
            'taf.foundation.api.cli',
            'taf.foundation.api.svc',
            'taf.foundation.api.ui',
            'taf.foundation.api.plugins',
            'taf.foundation.api.svc.REST',
            'taf.foundation.api.ui.patterns',
            'taf.foundation.api.ui.web',
            'taf.foundation.api.ui.mobile',
            'taf.foundation.api.ui.support',
            'taf.foundation.api.ui.controls',
            'taf.foundation.plugins.cli',
            'taf.foundation.plugins.svc',
            'taf.foundation.plugins.web',
            'taf.foundation.plugins.mobile',
            'taf.foundation.plugins.cli.paramiko',
            'taf.foundation.plugins.svc.requests',
            'taf.foundation.plugins.web.selenium',
            'taf.foundation.plugins.web.selenium.support',
            'taf.foundation.plugins.web.selenium.controls',
            'taf.foundation.plugins.mobile.appium',
            'taf.foundation.utils.traits',
            'taf.modeling.cli',
            'taf.modeling.svc',
            'taf.modeling.web',
            'taf.modeling.web.controls'
        ],
        namespace_packages = [],
        py_modules = [],
        classifiers = [],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [
            'enum34 >= 1.1.6',
            'paramiko >= 1.16.0',
            'PyYAML >= 3.11',
            'requests >= 2.9.1',
            'Appium-Python-Client >= 0.24'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = 'Automation Framework',
        python_requires = '',
        obsoletes = [],
    )
