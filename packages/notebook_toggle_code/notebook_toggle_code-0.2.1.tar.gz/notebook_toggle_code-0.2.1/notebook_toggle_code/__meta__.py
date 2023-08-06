
__name__ = 'notebook_toggle_code'
__packages__ = [__name__]

__version__ = '0.2.1'

__description__ = 'Alow user to toggle code cells - if notebook is trusted'
__author__ = 'oscar6echo'
__author_email__ = 'olivier.borderies@gmail.com'
__url__ = 'https://github.com/oscar6echo/{}'.format(__name__)
__download_url__ = 'https://github.com/oscar6echo/{}/tarball/{}'.format(__name__,
                                                                        __version__)
__keywords__ = ['python', 'display', 'javascript']
__license__ = 'MIT'
__classifiers__ = ['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6'
                   ]
__include_package_data__ = True
__package_data__ = {
    'templates':
    ['templates/bootstrapButtons.css',
     'templates/demoCalculator.html',
     'templates/main.html',
     'templates/notice_long.md',
     'templates/notice_safe.txt',
     'templates/notice_short.md',
     'toggleCode.js'
     ]
}
