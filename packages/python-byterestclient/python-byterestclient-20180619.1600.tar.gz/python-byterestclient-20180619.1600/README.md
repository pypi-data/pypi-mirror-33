python-restclient
================

A generic API Client

Building
========

1. Install the deps `pip install twine wheel`

2. Run `./buildme.sh`

3. Upload to the Byte repo

```bash
    dput --unchecked -c /etc/byte.cf wheezy ../CHANGESFILE
```

4. Upload to PyPI

```bash
    twine upload -r pypitest dist/*
```
