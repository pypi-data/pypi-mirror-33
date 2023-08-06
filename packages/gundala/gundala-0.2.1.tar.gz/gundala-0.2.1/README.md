# GUNDALA PROJECT

Gundala is an [EPP](https://en.wikipedia.org/wiki/Extensible_Provisioning_Protocol) 
(Extensible Provisioning Protocol) Client. It's provide a way to communicate 
between domain name registries and domain name registrars.

## Installing

At the time gundala only support Python3 or newer.

``` bash
pip3 install -U gundala
```

If you want to stay on bleeding edge version. Grab the code then
install it manually, using :

``` bash
pip3 install -r requirements.txt
pip3 install -e .
```

## Configuration Example

Duplicate file config.py.example to config.py

``` bash
cp example/config.py.example example/config.py
```

```python

config = {
    'host': 'someprovider.com',
    'port': 700,
    'user': 'username',
    'pass': 'password',
    'cert': 'somecertificate.pem'
}

contacts = {
    'registrant': 'idregistrant',
    'admin': 'idadmin',
    'tech': 'idtech',
}

namespaces = [
    'ns1.someprovider.com',
    'ns2.someprovider.com'
]

```

## Running

``` bash
python3 example/file_example.py
```
