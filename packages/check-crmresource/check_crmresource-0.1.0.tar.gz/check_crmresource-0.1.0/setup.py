from setuptools import setup, find_packages

setup(name='check_crmresource',
      description='Nagios plugin to check status of a CRM resource',
      version='0.1.0',
      url='https://gitlab.com/spike77453/check_crmresource',
      author='Christian Schürmann',
      author_email='spike@fedoraproject.org',
      license='GNU GPLv2+',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Plugins',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: System :: Networking :: Monitoring',
      ],
      packages=find_packages(),
      install_requires=[
          'nagiosplugin>=1.2',
      ],
      scripts=['bin/check_crmresource.py'],
)
