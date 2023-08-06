execsql.py
=========================

*Multi-DBMS SQL script processor.*

execsql.py is a Python program that applies a SQL script stored in a text file 
to a PostgreSQL, MS-Access, SQLite, MS-SQL-Server, MySQL, MariaDB, or Firebird 
database, or to an ODBC DSN.  execsql.py also supports a set of special 
commands (metacommands) that can import and export data, copy data between 
databases, and conditionally execute SQL statements and metacommands.  
These metacommands make up a control language that works the same across 
all supported database management systems (DBMSs). The metacommands are 
embedded in SQL comments, so they will be ignored by other script 
processors (e.g., psql for Postgres and sqlcmd for SQL Server).  The 
metacommands make up a toolbox that can be used to create both automated 
and interactive data processing applications.


Capabilities
=========================

You can use execsql to:

* Import data from text files or OpenDocument spreadsheets into a database.

* Copy data between different databases, even databases using different types of database management systems.

* Export tables and views as formatted text, comma-separated values (CSV), tab-separated values (TSV), OpenDocument spreadsheets, HTML tables, JSON, LaTeX tables, or unformatted (e.g., binary) data.

* Export data to non-tabular formats using several different template processors.

* View tables and views on the console or in a GUI dialog window.

* Conditionally execute different SQL commands and metacommands based on the DBMS in use, the database in use, data values, user input, and other conditions. Conditional execution can be used with the INCLUDE metacommand to implement loops.

* Use simple dynamically-created data entry forms to get user input.

* Write messages to the console or to a file during the processing of a SQL script, using metacommands embedded in SQL comments. These messages can be used to display the progress of the script or create a custom log of the operations that have been carried out or results obtained. Status messages and data exported in text format can be combined in a single text file. Data tables can be exported in a text format that is compatible with Markdown pipe tables, so that script output can be converted into a variety of document formats.

* Write more modular and maintainable SQL code by factoring repeated code out into separate scripts, parameterizing the code using substitution variables, and using the INCLUDE metacommand to merge the modules into a single script.

* Merge multiple elements of a workflow—e.g., data loading, summarization, and reporting—into a single script for better coupling of related steps and more secure maintenance.

Standard SQL provides no features for interacting with external files or 
with the user, or for controlling the flow of actions to be carried out
based either on data or on user input.  execsql provides these features
in a way that operates identically across all supported DBMSs on both
Linux and Windows.

execsql is inherently a command-line program that can operate in a completely 
non-interactive mode (except for password prompts). Therefore, it is suitable 
for incorporation into a toolchain controlled by a shell script (on Linux), 
batch file (on Windows), or other system-level scripting application. When 
used in this mode, the only interactive elements will be password prompts; 
passwords are not accepted on the command line or as arguments to the 
CONNECT metacommand. However, several metacommands can be used to generate
interactive prompts and data displays, so execsql scripts can be written to 
provide some user interactivity.

In addition, execsql automatically maintains a log that documents key 
information about each run of the program, including the databases that are 
used, the scripts that are run, and the user's choices in response to 
interactive prompts. Together, the script and the log provide documentation 
of all actions carried out that may have altered data.


Syntax and Options
========================


Commands
------------------------

    execsql.py -ta [other options] sql_script_file Access_db 

    execsql.py -tf [other options] sql_script_file Firebird_host Firebird_db

    execsql.py -tm [other options] sql_script_file MySQL_host MySQL_db 

    execsql.py -tp [other options] sql_script_file Postgres_host Postgres_db

    execsql.py -ts [other options] sql_script_file SQL_Server_host SQL_Server_db

    execsql.py -tl [other options] sql_script_file SQLite_db 


Arguments
--------------------------

     sql_script_file   The name of a text file of SQL commands to be executed. Required argument.

     Access_db         The name of the Access database against which to run the SQL.

     Firebird_db       The name of the Firebird database against which to run the SQL.

     Firebird_host     The name of the Firebird host (server) against which to run the SQL. 

     MySQL_db          The name of the MySQL database against which to run the SQL.

     MySQL_host        The name of the MySQL host (server) against which to run the SQL.

     Postgres_db       The name of the Postgres database against which to run the SQL.

     Postgres_host     The name of the Postgres host (server) against which to run the SQL. 

     SQL_Server_db     The name of the SQL Server database against which to run the SQL.

     SQL_Server_host   The name of the SQL Server host (server) against which to run the SQL. 

     SQLite_db         The name of the SQLite database against which to run the SQL.


Options
---------------------

    -a value        Define the replacement for a substitution variable $ARG_x. 
    -d value        Automatically make directories used by the 	EXPORT
                    metacommand: 'n'-no (default); 'y'-yes.
    -e value        Character encoding of the database. Only used for some 
                      database types. 
    -f value        Character encoding of the script file. 
    -g value        Character encoding to use for output of the WRITE and EXPORT
                    metacommands. 
    -i value        Character encoding to use for data files imported with the 
                    IMPORT metacommand. 
    -m              Display the allowable metacommands, and exit. 
    -p value        The port number to use for client-server databases. 
    -s value        The number of lines of an IMPORTed file to scan to diagnose 
                    the quote and delimiter characters. 
    -t value        Type of database: 
                          'p'-Postgres, 
                          'f'-Firebird, 
                          'l'-SQLite, 
                          'm'-MySQL or MariaDB, 
                          'a'-Access, 
                          's'-SQL Server, 
                          'd'-DSN connection.
    -u value        The database user name (optional). 
    -v value        Use a GUI for interactive prompts. 
    -w              Do not prompt for the password when the user is specified. 
    -y              List all valid character encodings and exit. 
    -z value        Buffer size, in kb, to use with the IMPORT metacommand 
                    (the default is 32).


Requirements
===========================

The execsql program uses third-party Python libraries to communicate with 
different database and spreadsheet software. These libraries must be 
installed to use those programs with execsql. Only those libraries that 
are needed, based on the command line arguments and metacommands, must 
be installed. The libraries required for each database or spreadsheet 
application are:

* PosgreSQL: psycopg2.

* SQL Server: pydobc.

* MS-Access: pydobc and pywin32.

* MySQL or MariaDB: pymysql.

* Firebird: fdb.

* DSN connections: pyodbc.

* OpenDocument spreadsheets: odfpy.

* Excel spreadsheets (read only): xlrd.

Connections to SQLite databases are made using Python's standard library, 
so no additional software is needed.

If the Jinja or Airspeed template processors will be used, those software
libraries must also be installed.




Copyright and License
================================

Copyright (c) 2007, 2008, 2009, 2014, 2015, 2016, 2017, 2018 R.Dreas Nielsen

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details. The GNU General Public License is available at
http://www.gnu.org/licenses/.
