# How to set-up access-control
There are two ways to control access, user/password authentication, and ip/domain checks. You can use either separately, or both.

## Turn on access control ##
The first thing you need to do to turn on access control is to set 
the variable `access_control` in `your_db_dir/data/web_config.cfg` to `True`, such as:

```Python
access_control = True
```

While this option turns on the ability to control access, you still need to configure authentication or ip check,
otherwise access control will be turned off.

## User authentication ##
To use user authentication, you need to create a logins.txt file inside your `your_db_dir/data/` directory. This can be a symlink.
If no file is found, access will be granted.
The logins.txt should one user/pass per line, separated by a tab, such as

```
username  password
another_user  another_password
```

## Domain and IP range check ##
To use this feature, you need to specify the location of the file in `web_config.cfg` in the `access_file` variable. 

This file should contain 3 Python variables: `domain_list`, `allowed_ips`,
`blocked_ips`. Each variable should be a list containing the salient info.

The `domain_list` variable should be a list of domains allowed to access you database.
```Python
domain_list = [
  "uchicago.edu",
  "indiana.edu",
  "louisiana.edu",
  "northwestern.edu"
] 
```

The `allowed_ips` variable is a list of ips which are given access to the DB. Note that these are 
matched using a regular expression, so you can express the whole ip, or just a part of it.
```Python
allowed_ips = [
  "128.135.",
  "128.32",
  "136.152",
  "136.153.1.1-255"
]
```
Note that the last IP notation expresses an IP range.

The `blocked_ips` variable is a list of IPs (exact matches needed) to deny access to:
```Python
blocked_ips = [
  "1.1.1.4"
]
```
