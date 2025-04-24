---
title: Create New TEC Project
menuTitle: Create New TEC Project
weight: 5
---

For admins, create a new project is simple.

Use the command line tool [create-tec-project](https://svl-devops-gitlab01.fortilab.fortinet.com/tec/create-tec-project) to create a new TEC project.

Follow the instructions in the [README of create-tec-project](https://svl-devops-gitlab01.fortilab.fortinet.com/tec/create-tec-project).

```sh
./create-tec-project -h
Usage of create-tec-project:
        -name
                name of the project in gitlab
        -group
                gitlab group of the project, must be a sub-group in tec-content
        -title
                optional, display title of the project
        -description
                optional, long descriptino of this project
        -theme
                optional, theme of the project
        -maintainer
                optional, username of the maintainer
        -src_name
                optional, source project name to copy content from
        -src_group
                optional, source project group to copy content from, must be a sub-group in tec-content
        -add_to_tec
                flag, add project to tec homepage after done

./create-tec-project -group devops -name test-project
./create-tec-project -group devops -name test-project-2 -maintainer jingshao
./create-tec-project -group devops -name new-user-guide -src_group devops -src_name tec-user-guide

```
