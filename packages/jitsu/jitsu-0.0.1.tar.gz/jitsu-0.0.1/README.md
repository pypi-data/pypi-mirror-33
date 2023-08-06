# jitsu - jinja2 rendering with yaml

Simple, easy rendering of templates for each data file, with one command.

## What jitsu does?

`jitsu` renders data in each data file to specified jinja2 template, and
then store the results in a new directory `_dist`.

## Usage

1. Installation: `pip install jitsu`
2. Directory structure:
   1. All the templates go to `templates` directory. (Can also be specified with
      `-t` option)
   2. All the data files go to `data` directory. (Can also be specified with `-d` option.)
3. Run `jitsu`.

## Applications

### Static websites

```
templates/
 `-- blog-post.j2
  |- poem-post.j2
data/
 `-- post1.yaml
  |- post1.yaml
  |- post2.yaml
  |- post3.yaml
  |- post4.yaml
  |- poem1.yaml
  |- poem2.yaml
```

Running `jitsu` will give something like this
```
_dist/
 `-- post1.html
  |- post2.html
  |- post3.html
  |- post4.html
  |- poem1.html
  |- poem2.html
```
