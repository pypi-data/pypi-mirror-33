# Python client to the ITS Private Cloud API

[![CI][build-img]](https://gitlab-ee.eis.utoronto.ca/vss/py-vss/commits/master)
[![Coverage][coverage-img]](https://gitlab-ee.eis.utoronto.ca/vss/py-vss/commits/master)
[![PyPI][pypi-img]](https://pypi.python.org/pypi/pyvss)
[![PyPI version][pyver-img]](https://pypi.python.org/pypi/pyvss)
[![Docker Image Pulls][docker-pulls-img]][docker-image]
[![Docker Image Layers][docker-layer-img]][docker-image]
[![Docker Image Version][docker-version-img]][docker-image]

   
## Documentation

Package documentation is now available at [docs][docs].

## Installation

The fastest way to install PyVSS is to use [pip][pip]:

```bash
pip install pyvss
```

If you have PyVSS installed and want to upgrade to the latest version you can run:

```bash
pip install --upgrade pyvss
```

This will install PyVSS as well as all dependencies. 

You can also just [download the tarball][download the tarball]. Once you have the `py-vss` directory structure on your workstation, you can just run:

```bash
cd <path_to_py-vss>
python setup.py install
```

### macOS

XCode is required if you are planning to interact with VSKEY-STOR via [WebdavClient][WebdavClient].

```bash
xcode-select --install
curl https://bootstrap.pypa.io/ez_setup.py -o - | python
python setup.py install --prefix=/opt/setuptools
sudo easy_install pyvss
sudo easy_install webdavclient
```

### Linux

Additional libraries are required iif you are planning to interact with VSKEY-STOR via [WebdavClient][WebdavClient].

```bash
sudo apt install libxml2-dev libxslt-dev python-dev
sudo apt install libcurl4-openssl-dev python-pycurl
sudo easy_install pyvss
sudo easy_install webdavclient
```

### Windows

> Windows users, download and install [Python Releases for Windows][Python Releases for Windows] prior running [pip][pip].

Microsoft Visual Studio Express or Microsoft Visual C++ is required if you are planning
to interact with VSKEY-STOR via [WebdavClient][WebdavClient].

```powershell
easy_install.exe pyvss
easy_install.exe webdavclient
```

## Docker

For more information refer to the [Docker](docker/README.md) section.

Use
===

Create an instance of ``VssManager`` passing your **ITS Private Cloud API access token**
and your are all set to start calling any of the self-descriptive methods included:

```python
from pyvss.manager import VssManager
vss = VssManager(tk='api_token')

# list vms
vms = vss.get_vms()

# list folders
folders = vss.get_folders()

# networks
networks = vss.get_networks()

# domains
domains = vss.get_domains()

# power cycle vm
vss.power_cycle_vm(uuid='<uuid>')
   
# create vm
req = vss.create_vm(os='ubuntu64Guest', built='os_install',
                    description='Testing python wrapper',
                    folder='group-v6736', bill_dept='EIS', disks=[100, 100])
uuid = vss.wait_for_request(req['_links']['request'], 'vm_uuid', 'Processed')

# creating multiple vms
reqs = vss.create_vms(count=3, name='python', os='ubuntu64Guest', bill_dept='EIS',
        description='Testing multiple deployment from python wrapper',
        folder='group-v6736', built='os_install')
uuids = [vss.wait_for_request(r['_links']['request'], 'vm_uuid', 'Processed') for r in reqs]

# power on recently created vms
for uuid in uuids:
   vss.power_on_vm(uuid)
        
# create snapshot
req = vss.create_vm_snapshot(uuid='5012abcb-a9f3-e112-c1ea-de2fa9dab90a',
                             desc='Snapshot description',
                             date_time='2016-08-04 15:30',
                             valid=1)
snap_id = vss.wait_for_request(req['_links']['request'], 'snap_id', 'Processed')

# revert to snapshot
req = vss.revert_vm_snapshot(uuid, snap_id)
```

An alternative is to generate a token from within the ``VssManager`` class and this can be done
by setting the following environment variables

```bash
export VSS_API_USER='username'
export VSS_API_USER_PASS='username_password'
```

Then, from the ``VssManager`` call the ``get_token`` method as follows:

```python
from pyvss.manager import VssManager
vss = VssManager()
vss.get_token()
```   

## Getting Help

We use GitLab issues for tracking bugs, enhancements and feature requests.
If it turns out that you may have found a bug, please [open a new issue][open a new issue].

## Versioning

The API versions are tagged based on [Semantic Versioning](https://semver.org/). Versions available in the 
[tags section](https://gitlab-ee.eis.utoronto.ca/vss/py-vss/tags).

## Contributing

Refer to the [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process of 
submitting code to the repository.

[docs]: https://eis.utoronto.ca/~vss/pyvss/
[download the tarball]: https://pypi.python.org/pypi/pyvss
[Click]: http://click.pocoo.org/6/
[Python Releases for Windows]: https://www.python.org/downloads/windows/
[pip]: http://www.pip-installer.org/en/latest/
[open a new issue]: https://gitlab-ee.eis.utoronto.ca/vss/py-vss/issues/new>
[WebdavClient]: http://designerror.github.io/webdav-client-python/
[Alpine Linux]: https://hub.docker.com/_/alpine/
[PyVSS]: https://pypi.python.org/pypi/pyvss
[build-img]: https://gitlab-ee.eis.utoronto.ca/vss/py-vss/badges/master/build.svg
[coverage-img]: https://gitlab-ee.eis.utoronto.ca/vss/py-vss/badges/master/coverage.svg
[pypi-img]: https://img.shields.io/pypi/v/pyvss.svg
[pyver-img]: https://img.shields.io/pypi/pyversions/pyvss.svg
[docker-pulls-img]:  https://img.shields.io/docker/pulls/uofteis/pyvss.svg
[docker-layer-img]: https://images.microbadger.com/badges/image/uofteis/pyvss.svg
[docker-version-img]: https://images.microbadger.com/badges/version/uofteis/pyvss.svg
[docker-image]: https://hub.docker.com/r/uofteis/pyvss/
