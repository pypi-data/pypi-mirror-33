# stilt
Python project configreator.

There are other Python template projects out there. This one has a specific audience in mind and is probably not the one you are looking for.

## Installing to use stilt
```
$ pip3 install stilt
$ python3 -m stilt.project <path/to/project>
```

## Installing to develop stilt
```
$ pip3 install --user virtualenv
$ git clone https://github.com/bdube/stilt.git
$ cd stilt
$ virtualenv venv
$ source venv/bin/activate
  or run venv\Scripts\activate on Windows
$ pip3 install -r requirements.txt
$ pip3 install -e .
$ python3 -m stilt.project <path/to/project>
```
