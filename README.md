### templar [WIP]

Dead simple template engine in Python

Example 1:

```python

from templar import Templar

t = Templar()
t.compile('Hey Templar is {{remark}}')
rendered = t.render({'remark':'awesome'})

```

Output

```
Hey Templar is awesome
```

Example 2:

```python

from templar import Templar

t = Templar()
t.compile('Greetings! {% for n in names %} Hi n {% endfor %}')
rendered = t.render({'names':['alice', 'bob', 'malice']})

```

Output
```
Greetings! Hi alice
Hi bob
Hi malice

```
