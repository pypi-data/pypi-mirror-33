# 1
may,use like this

# 2
```
dir1:
    file1.py
dir2:
    file2.py
```

# 3
file2.py:

```
import file1
```

# 4
python dir2/file2.py

you will got: ERROR,ERROR,ERROR ...

# 5

file2.py

```
if __name__ == '__main__':
    import smart_append_path
    smart_append_path.append_top1(__file__)
```
