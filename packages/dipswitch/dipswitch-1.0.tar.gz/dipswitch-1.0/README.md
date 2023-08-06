# Dipswitch

Dipswitch is a Python module allowing for switch-case statements with a
similar structure to those in languages that natively support them.

## Usage

```
from dipswitch import switch
for case in switch(2):
	if case(0):
		print("doesn't execute")
	if case(1):
		print("doesn't execute")
		break
	if case(2):
		print("executes")
	if case(3):
		print("executes")
		break
	if case(4):
		print("doesn't execute")
		break
	if case.default():
		print("doesn't execute")
```

