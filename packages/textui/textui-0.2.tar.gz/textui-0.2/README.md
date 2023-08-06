# Python textui package
Text-based UI builder for Python

Full documentation provided at https://firsttempora.github.io/Python-textui/

## Quickstart

Install from `pip`: `pip install --user textui`

The `uielements` module contains individual `user_*` functions that can be 
used to interactively get values:

```
from textui import uielements

>>> uielements.user_input_list('Choose your favorite fruit', ['Apple', 'Banana', 'Cherry'])
Choose your favorite fruit
A empty answer will cancel.
   1: Apple       2: Banana       3: Cherry    
Enter 1-3: 2
'Banana'

>>> uielements.user_input_date('When did the Eagle land on the moon?')
When did the Eagle land on the moon?
Enter in one of the formats: yyyy-mm-dd
Entering nothing will cancel
--> 1969-07-20
datetime.datetime(1969, 7, 20, 0, 0)
```

`uielements` also contains a series of `opt_user_*` functions that will decide if the
user needed to be queried based on the given value, or check is the value is valid:

```
# If the value None is given, it is assumed 
# that the user need to provide a value
>>> uielements.opt_user_input_list('Choose your favorite fruit', None, ['Apple', 'Banana', 'Cherry'])
Choose your favorite fruit
A empty answer will cancel.
   1: Apple       2: Banana       3: Cherry    
Enter 1-3: 2
'Banana'

# If a non-None value is given, it is checked.
# So long as it is valid, it is returned.
>>> uielements.opt_user_input_list('Choose your favorite fruit', 'Apple', ['Apple', 'Banana', 'Cherry'])
'Apple'

# If not valid, an error is raised automatically
>>> uielements.opt_user_input_list('Choose your favorite fruit', 'Watermelon', ['Apple', 'Banana', 'Cherry'])
Error thrown using UIErrorWrapper
UIValueError: The value Watermelon is invalid. It must be one of: Apple, Banana, Cherry
```
