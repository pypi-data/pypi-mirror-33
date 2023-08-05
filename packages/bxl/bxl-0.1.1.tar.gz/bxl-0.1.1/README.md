# Basic/Barcelona/Bizarre XNAT Library (BXL)

BXL is a library for interacting with the REST interface of XNAT ([Extensible Neuroimaging Archive Toolkit](https://www.xnat.org/)),
an open-source imaging informatics software platform.

## Usage

### Installation

With [pip](https://pypi.org/project/pip/) package management system:
```commandline
 git clone https://gitlab.com/bbrc/xnat/bxl.git .
 cd ./bxl
 python setup.py sdist bdist_wheel
 pip install ./dist/bxl-0.1.1.tar.gz 
```

Without pip:
```commandline
 git clone https://gitlab.com/bbrc/xnat/bxl.git .
 cd ./bxl
 python setup.py install
  
```

### Credentials handling

The `xnat.Connection()` class constructor expects a `credentials` argument to be passed when instantiated, 
* If is a `tuple`, it will proceed to a basic authentication procedure against the `host` XNAT instance.
* If is a `basestring`, it will reuse it as a cookie for authentication against the `host` XNAT instance.   
* Otherwise (or if authentication procedure failed in the aforementioned cases), it will remain offline. 

### Examples 

Connect to XNAT instance using an existing JSESSIONID token and get a list of user-visible XNAT projects
```python
 import bxl.xnat as xlib
 
 c = xlib.Connection(hostname='http://myxnat.org',credentials='1A12346385E876546C99B4179E20986A')
 
 data = c.get_json_data(URL=c.host + '/data/projects')
 projects = { item['ID'] : item['URI'] for item in data }
 print projects
 
 c.close_jsession()            
  
```

Connect via ['with' statement](https://docs.python.org/2.5/whatsnew/pep-343.html) to create a new Female subject 'dummy' in the 'test' project
```python
 from bxl import xnat
 
 with xnat.Connection(hostname='http://myxnat.org',credentials=(usr,pwd)) as c :
     response = c.put_data(URL=c.host + '/data/projects/test/subjects/dummy', data="",options= {'gender' : 'female'} )
     subject_uid = response.content
     print 'New subject %s created!' %subject_uid
 
```