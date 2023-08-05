# monpyou
Python library to read account information from the [moneyou](https://www.moneyou.de/) bank.

Right now the library only supports reading the balance of an account.

# Usage
A simple usage example:

```python
from monpyou import MonpYou

mpy = MonpYou(username, password)
mpy.update_accounts()
for account in mpy.accounts:
    print("{} ({}): {} {}".format(account.name, account.iban, account.balance, account.currency))
```
See also [monpyou_demo](monpyou_demo).

# License
Licensed under the Apache License, Version 2.0 (the "License");

you may not use this project except in compliance with the License.
You may obtain a copy of the License at 
http://www.apache.org/licenses/LICENSE-2.0

# Disclaimer
This project is not supported in any way by moneyou. Use it at your own risk!
