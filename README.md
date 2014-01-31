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

list all your surveys

	qualpy list

#### download

downloads your survey and panel results in csv format

###### download all active surveys

    qualpy download --survey all --out PATH/TO/DOWNLOAD/DIR

###### download a particular survey

	qualpy download --survey SV_a3Ad245ADdaf --out PATH/TO/DOWNLOAD/DIR

###### download all panels

	qualpy download --panel all --out PATH/TO/DOWNLOAD/DIR

#### document

generates an html data dictionary of your surveys (tables) and questions (columns)

    qualpy document --out PATH/TO/DOC.html
