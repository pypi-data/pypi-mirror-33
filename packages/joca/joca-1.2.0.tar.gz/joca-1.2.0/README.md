# joca
Jira On Call Assignee

Check an ical url (files not supported yet) for current on call.

[PyPI](https://pypi.org/project/joca/)

# Installation

```
pip install joca
```

# Configuration file

The configuration holds 3 sections, `local`, `jira` and `projects`.

- `local` is for configuring logging and where the config file's schema is located for validation.
- `jira` houses the username, password and server url of the Jira instance joca connects to.
- `projects` is a list of objects that tell joca what project, what ical and the regex to apply to the event summary to extract the users name.

Here is a basic configuration:

```
{
    "local": {
        "logging": {
            "file": "/var/log/joca.log",
            "format": "%(asctime)s %(levelname)s %(message)s",
            "level": "info"
        },
        "schema": "/etc/joca.config.json.schema"
    },
    "jira": {
        "server": "https://instance.jira.com",
        "username": "api-user",
        "password": "hunter2"
    },
    "projects": [
        {
            "key": "PROJ",
            "ical": "https://totally.a-website.com/calendar",
            "regex": "^(.*)$"
        }
    ]
}
```

- `local.logging`, `format` is not required.
- `local.logging.level` doesn't need to be uppercase.
- `projects.#.key` doesn't have to be uppercase, joca will handle that.

`projects` is a list, so feel free to have multiple projects set up, and it will loop over them.

# To do

Check out todo.txt for the basic list of to-do's.

todo.txt follows the syntax rules laid out [here](https://github.com/todotxt/todo.txt).

# Version Numbering

joca follows the three major tenets of [SemVer](https://semver.org/spec/v2.0.0.html).

> Given a version number MAJOR.MINOR.PATCH, increment the:
>
> - MAJOR version when you make incompatible API changes,
> - MINOR version when you add functionality in a backwards-compatible manner, and
> - PATCH version when you make backwards-compatible bug fixes.
>
> Additional labels for pre-release and build metadata are available as extensions to the MAJOR.MINOR.PATCH format. (Preston-Warner, 2013)

Build metadata MAY be denoted by appending a hyphen and a series of dot separated identifiers immediately following the patch or pre-release version.

Build version follows [RFC-1912 section 2.2](https://tools.ietf.org/html/rfc1912#section-2.2):

> The recommended syntax is YYYYMMDDnn
> (YYYY=year, MM=month, DD=day, nn=revision number.  This won't
> overflow until the year 4294" (Barr, 1996)

Example: `1.23.4-2018033000`:

- Major version `1`
- Minor version `23`
- Patch version `4`
- Build number `2018033000` => `2018` `03` `30` `00`

Please read the full spec at the link above or in the citations.

# Citations

Preston-Warner, T. (2013). _Semantic Versioning 2.0.0_. Retrieved November 27, 2017, from
    https://semver.org/spec/v2.0.0.html

Barr, D. (1996). _Common DNS Operational and Configuration Errors_. Retrieved on March 30, 2018,
    from https://tools.ietf.org/html/rfc1912#section-2.2
