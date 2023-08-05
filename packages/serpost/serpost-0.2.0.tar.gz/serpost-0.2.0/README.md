# Serpost CLI
[![Build Status](https://travis-ci.org/erickgnavar/serpost.svg?branch=master)](https://travis-ci.org/erickgnavar/serpost)

CLI tool for search tracking number in SERPOST page, works in python 2 and python 3

### Install

```
pip install serpost
```

### Usage

```
serpost-cli {tracking-code-1}
serpost-cli {tracking-code-1} {tracking-code-2}
```

#### Example

```
serpost-cli 123
```

#### Output
```
Tracking number: 123
--------------------
15/08/2014 03:00 | ENVIO INGRESA A LA OFICINA CENTRAL DE Peru                                                          
15/08/2014 03:08 | DISPONIBLE PARA SALIR A United States of America (the)                                              
```

### TODO:

- [ ] Add tests
- [ ] Better error handling
- [ ] Add a logger
