# Eve-CLI

Python-Eve Client - A lib to easily communicate with an Eve API server.


## Installation

```sh
> pip install -e .
```

## Example

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from eve_cli.client import EveClient
from eve_cli.document import BaseDocument


TOKEN = os.getenv('TOKEN', 'BAD_TOKEN')


class Project(BaseDocument):

    name = "string"
    description = "string"

    def __str__(self):
        return ("{}<_id={},\n\t_created={},\n\t_updated={},\n\t_etag={},\n\tname={},\n\tdescription={}>"
                .format(self.__class__.__name__,
                        self._id,
                        self._created,
                        self._updated,
                        self._etag,
                        self.name,
                        self.description))


client = EveClient(url="http://localhost:1337/",
                   headers={"Authorization": TOKEN})
client.register_resource(Project)

for project in client.project.iterate(max_results=10): # List projects
    print(project._id)

for project in client.project.iterate(max_results=10): # Delete projects
    client.project.delete(project._id, project._etag) 

print(len(client.project.search()))

project = client.project.create(name="Test", description="Test Description")

print(project._id)

project = client.project.get(_id=project._id) # Retrieve full project since eve don't return project field in the POST response

```
