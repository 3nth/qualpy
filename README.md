# qualpy
your Qualtrics buddy

## qualpy needs

#### your authentication info

qualpy takes a config file. 

######qualpy.ini

	[account]
	user = someone@somewhere.com
	token = tDF5xbafdnWShsdBHSDGHaF
	library_id = UR_4afh5s3fbadfh34

it's searched for in the following order:

1. argument: --config=path
2. qualpy.ini in cwd
3. qualpy.ini in home directory (~ or %HOME%)

## qualpy does

#### list

list all surveys

	qualpy list

#### download

downloads the results in csv format for all active surveys

    qualpy download --out PATH/TO/DOWNLOAD/DIR
        
you'll get a file per survey

#### document

generates an html document describing the surveys (tables) and questions (columns)

        qualpy document --out PATH/TO/DOC.html
        
you'll get a really simple single page html file with the basic details
