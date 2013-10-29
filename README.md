# qualpy
your Qualtrics buddy

## qualpy needs

#### your authentication info

It's provided as a filepath at the command line (--auth). 

The file should have two lines: 1) username 2) api token

        me@somewhere.com
        asdfasdfgq4t14gavr1342tqer


## qualpy does

#### download

downloads the results in csv format for all active surveys

        qualpy --auth=PATH/TO/AUTH download PATH/TO/DOWNLOAD/DIR
        
you'll get a file per survey

#### document

generates an html document describing the surveys (tables) and questions (columns)

        qualpy --auth=PATH/TO/AUTH download PATH/TO/DOC.html
        
you'll get a really simple single page html file with the basic details
