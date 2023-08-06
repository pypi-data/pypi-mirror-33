from distutils.core import setup
setup(
  name = 'pipulate',
  packages = ['pipulate'],
  version = '0.1.91',
  download_url = 'https://github.com/miklevin/pipulate/archive/0.1.9.tar.gz',
  description = 'Use Google Sheets for Marketing Dashboards Free',
  long_description='Light framework to help do manipulate Google Sheets as Pandas Dataframes. Useful for SEO and Social Media Dashboards.',
  author = 'Mike Levin SEO, 360i and Commodore Computers alum in NYC & Inventor of HitTail keyword tool.',
  license='MIT',
  author_email = 'miklevin@gmail.com',
  url = 'https://github.com/miklevin/pipulate',
  python_requires='>=3',
  install_requires=['gspread', 'httplib2', 'google-api-python-client'],
  keywords = ['seo', 'datamaster', 'data master', 'google', 'sheets', 'pandas', 'gspread', 'google data', 'google sheets', 'google spreadsheets', 'google sheet', 'google spreadsheet', 'spreadsheets', 'spreadsheet', 'database', 'databases', 'datascience', 'data science']
)

classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Marketing',
	'Topic :: Data',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7'
]
