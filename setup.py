from distutils.core import setup
setup(
  name = 'evemarkettools',         
  packages = ['evemarkettools'],   
  version = '1.4',      
  license='MIT',        
  description = 'Provides a variety of functions to extract market information from the EVE ESI',  
  author = 'Filip Jöde',                   
  author_email = 'joede.filip@gmail.com',      
  url = 'https://https://github.com/SustainedCruelty/evemarkettools',  
  download_url = 'https://github.com/SustainedCruelty/evemarkettools/archive/v0.1.tar.gz',   
  keywords = ['EVE Online', 'API', 'EVE ESI','Swagger'], 
  install_requires=[],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)