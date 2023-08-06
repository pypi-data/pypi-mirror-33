# What is Xalanih ?

Xalanih is a python script made to help you version your SQL database. You can use it to manage the creation or update the database of your project.

# Technical Requirements
- Python 3.6
- mysqlclient
- sqlparse

# How to install Xalanih

```
pip3 install xalanih
```

# How to use Xalanih

## Create the db

```Bash
python3 -m xalanih create <database>
```
where \<database\> must be replaced by the name of the database.

## Update the db

```Bash
python3 -m xalanih update <database>
```
where \<database\> must be replaced by the name of the database.

## Options

Differents options can be given to the script. You can find all of them using the following command:

```
python3 xalanih -h
```

### Working directory

```
-d <directory>
```

Specify the directory where all the database scripts are.

**Default value**: "."

### Database type

```
-t <type>
```

Specify the type of database to which the script has to connect.

**Accepted value**: mysql | **Default value**: mysql

### Host

```
-H <host>
```

The address of the host of the database.

**Default value**: localhost

### Port

```
-p <port>
```

The port of the database.

**Default value**: 3306

### User

```
-u <user>
```

The user used to connect

**Default value**: root

### Password

```
-pwd <password>
```

The password used to connect to the database.

### Socket

```
-s <socket>
```

The path to the mysql socket if it is not at the default location *(/tmp/mysql.sock)*.

### Logging

These options are linked to the logging.

#### Verbosity

```
-v <verbosity>
```

The verbosity of the logs in standard output.

**Accepted values**: 0,1,2,3,4 | **Default value**: 3

- **0**: No logs.
- **1**: Only errors.
- **2**: Errors and warnings.
- **3**: Informations, warnings and errors.
- **4**: Debugs, informations, warnings and errors.

#### Log file

```
-l <filename>
```

The name of the file where the logs are saved. It is not affected by the verbosity options (It is always set at 4). If no file specified, no file are created.

### last update

```
-to <update>
```

Define the last update that will be applied. Must be an update not included in `included_updates`.

### no update

```
-nu
```

Has only an effect with the create option. If specified, the script will only execute the creation script and will not apply the updates.

# How to structure the directory containing the database scripts

The structure to use for the directory that contains all the scripts you have for your database.

```
L creation (directory)
    L  creation.sql (file)
    L  included_updates (file)
L update (directory)
    L  script01.sql (file)
    L  ...
```

## creation *(directory)*

The **creation** directory will contains the scripts that will be used to create the baseline of the database. These will only be called when the database is created from zero. That means that they will not be used in case of a database update.

### creation.sql *(file)*

The script **creation.sql** is the entrypoint of Xalanih to create the database. This file must contains all the needed script to create the baseline of your database.

### included_updates *(file)*

When you will have a lot of update file, you will want to create the database directly with these modification instead of applying them after. In order to do that, you will have to add the modification directly to your *creation.sql*. But in order for Xalanih to not apply the update scripts, you have to add the name of all update scripts already integrated to the file **included_updates**. There should be one filename by line.

## update *(directory)*

The **update** directory must contains all your update scripts (and nothing else). There is not realy a nomenclature for the update scripts but the alphabetical order should correspond to their chronological order. Also, no patch can be named *initial_install*. This is because this name is associated to the creation of the database

# Table created by xalanih: xalanih_updates

The table xalanih_patches contains 3 columns:
id, update_name, and update_apply_time.
It is used by the script to detect which patches have already been applied. The patch name associated to the initial creation of the database is **initial_install**.
