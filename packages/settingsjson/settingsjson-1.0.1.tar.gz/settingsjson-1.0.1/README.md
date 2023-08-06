# settingsjson.py

[![PyPI](https://img.shields.io/pypi/v/settingsjson.svg)](https://pypi.org/project/settingsjson/)

simple setting json getter

## how to use

```sh
pip install settingsjson
```

* write settings to `.settings.json`

```JSON
{
	"DB_PATH": "postgresql://user:seacret@host:port/dbname"
}
```

* read settings from your apps

```py
from sqlalchemy import create_engine
import settingsjson

settings = settingsjson.get()
db = create_engine(settings["DB_PATH"])
```

```
echo ".settings.json" >> .gitignore
```
