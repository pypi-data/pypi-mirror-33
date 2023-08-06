#
#distutils is used just for creating python source distributions and c extension
#setuputils is a downloadable pip package
#from distutils.core import setup, Extension
from setuptools import setup

c = [
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: Apache Software License',
    #
    #'Environment :: Web Environment',
    'Environment :: Win32 (MS Windows)',
    'Environment :: Console',
    #
    'Natural Language :: English',
    #
    'Operating System :: Microsoft',
    'Operating System :: Microsoft :: Windows :: Windows 8',
    #
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3 :: Only',
    #
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Other Audience',
    'Intended Audience :: Science/Research',
    #
    'Topic :: Education',
    'Topic :: Games/Entertainment',
    'Topic :: Scientific/Engineering :: Mathematics',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities'
]

#Extension-describes a single C or C++ extension module in a setup script.
#mod = Extension('helloworld',   #extension name
    #include_dirs=[],    #	list of directories to search for C/C++ header files (in Unix form for portability)
    #library_dirs=[],    #	list of directories to search for C/C++ libraries at link time
    #define_macros=[],  #list of macros to define; each macro is defined using a 2-tuple (name, value), where value is either the string to define it to or None to define it without a particular value (equivalent of #define FOO in source or -DFOO on Unix C compiler command line)
    #libraries=[],       #list of library names (not filenames or paths) to link against
    #runtime_library_dirs   #list of directories to search for C/C++ libraries at run time (for shared extensions, this is when the extension is loaded)
    #extra_objects=[]    #list of extra files to link with (eg. object files not implied by ‘sources’, static library that must be explicitly specified, binary resource files, etc.
    #depends=[]         #list of files the extension depends on
    #license	='This is mine not yours!',
    #sources:list of source filenames,
    #relative to the distribution root (where the setup script lives),
    #in Unix form (slash- separated) for portability.
    #Source files may be C, C++, SWIG (.i), platform-specific resource files,
    #or whatever else is recognized by the build_ext command as source for a Python extension.
    #sources = ['pyExt.c'])  

   
lic=''
desc=''   

with open('README.md') as f:
    desc = f.read()
    
with open('LICENSE.md') as f:
    lis = f.read()
    
#setup() creates a Distribution instance
pack = {
    'name':'integerSequence',    #package name
    'version':'0.1.1',  #package version
    'author':'Tyler R. Drury',
    'author_email':'that_canadianguy@hotmail.com',
    'maintainer':'Tyler R. Drury',
    'maintainer_email':'that_canadianguy@hotmail.com',
    'url':"https://github.com/vigilance91/integerSequences-py",
    'license':lic,
    #'url':'',  #url for package homepage email(doxygen site)
    #'download_url':''  #url where package can be downloaded (GitHub)
    'description':'A Package for natively representing and calculating common integer sequences',
    'long_description':desc,    #'Series include: factorials, prime, catalan, collatz, pronic, hofstadter, horadam, padovan and geometric number series', #long_desc
    'long_description_content_type':"text/markdown",
    #'keywords':'integer sequences catalan collatz pronic factorial prime mersenne padovan hofstadter horadam polygonal pell lucas fibonacci',
    'data_files':[('', ['README.md', 'LICENSE.md'])], #list of data files to install with package, relative to setup.py, include readme and license with source distribution
    'packages':['integerSequence'],
    'classifiers':c
    #include_package_data=True
    #'py_modules':[]  #  	A list of Python modules that distutils will manipulate
    #'scripts':['timer']   #A list of standalone script files to be built and installed
    #'ext_modules':[mod] #A list of Python extensions to be built, instances of distutils.core.Exension
}
#dis = 
setup(**pack)