# qualpy
your Qualtrics buddy

## Authentication
qualpy needs your authentication information. It's provided as a filepath at the command line (--auth). The file should have two lines

1. username
2. api token

    me@somewhere.com
    asdfasdfgq4t14gavr1342tqer


## Actions
qualpy does the following.

download - downloads the results in csv format for all active surveys.
document - generates an html document describing the surveys (tables) and questions (columns)