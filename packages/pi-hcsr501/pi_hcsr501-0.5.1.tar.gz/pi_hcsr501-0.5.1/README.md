# pi_hcsr501
[![Build Status](https://travis-ci.org/kangasta/pi_hcsr501.svg?branch=master)](https://travis-ci.org/kangasta/pi_hcsr501)

Library for playing around with hcsr501 PIR motion sensor with Raspberry Pi.

## Usage

```python

from pi_hcsr501 import HcSr501

HCSR501 = HcSr501()

while True:
	print(str(HCSR501.active) + " ", end="\r")
	sleep(0.5)

```

## Testing

Run unit tests with command:

```bash
cd pi_hcsr501

python3 -m unittest discover -s tst/
```

Get test coverage with commands:
```bash
cd pi_hcsr501

coverage run -m unittest discover -s tst/
coverage report -m
```
