## Description

A simple django app that is based on a database design for a volunteer organisation.
In the app there is the ability to manage tasks, volunteer teams, events, expenses and incomes.

## Installation Instructions

### Requirments

django, matplotlib

```bash
$ git clone https://github.com/Vagos/volunteer-organisation-app
$ cd volunteer-organisation-app

$ make # create the database
$ make clean # remove the database

$ python volunteer_organisation/manage.py runserver
```

Head over to: http://127.0.0.1:8000/
