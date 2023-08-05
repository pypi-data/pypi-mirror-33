from setuptools import setup

setup(
    name="rs3clans",
    description='A Python 3 module wrapper for RuneScape 3 Clan\'s API',
    long_description='''# rs3clans.py
A Python 3 module wrapper for RuneScape 3 Clan's API

Current Version: 0.3.1

***

## Setup:

```bash
python3 -m pip install rs3clans
```

***

### Usage:

* Import:

```python3
import rs3clans
```

***

* Getting a full clan list (type: csv.reader):

```python
rs3clans.get_clan_list('clan_name')
```

- You can iterate through clan lists as you normally would

***

* Getting a clan's total exp (type: int):

```python
rs3clans.get_clan_exp('clan_name')
```

***

* Getting a user's total clan exp (type: int):

```python
rs3clans.get_user_clan_exp('user_name', 'clan_name')
```

***

* Getting a user's clan rank (type: string):

```python
rs3clans.get_user_rank('user_name', 'clan_name')
```

***

* Getting a user's clan Name, Rank, Clan Exp and Kills (type: list)

```python
rs3clans.get_user_info('user_name', 'clan_name')
```

- You can use specific elements of the list as you normally would or use it as whole

***

* Getting the total player count of a Clan (type: int):

```python
rs3clans.get_player_count('clan_name')
```

***

* Getting the average clan exp per player in a Clan (type: float):

```python
get_average_clan_exp('clan_name')
```
    ''',
    long_description_content_type='text/markdown',
    version='0.3.1',
    author='John Victor',
    author_email='johnvictorfs@gmail.com',
    license='MIT',
    packages=['rs3clans'],
    zip_safe=False,
    url='https://github.com/johnvictorfs/rs3clans.py',
    classifiers = (
        "Programming Language :: Python :: 3"
    )
)
