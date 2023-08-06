# rkpython
# Various functions for personal use

# dependencies
import os

# rk.to_txt()

def to_txt(l, path = 'text_file.txt', overwrite = False, verbose = False):

#Docstring
	'''
	Saves a list to a .txt file.

	--------------
	
	l : list, default is None
		List object to be saved.  
	
	path : str, default is 'text_file.txt'
		File path (with file name) you want to save to.  
	
	overwrite : bool, default is False  
		Overwrites the file if it exists.
		
	verbose : boolean, default is False
		Prints out a message if the operation was succesful
		
	--------------

	Examples :
	
	rk.to_txt(var_list, './Documents/vars.txt', verbose = True)
	>> File successfully written to ./Documents/doc.txt
	'''
	
    if type(l) == list:
        if overwrite == True:
            try: 
                with open(path, 'w') as file:
                    for obj in l:
                        file.write("%s\n" % obj)
                if verbose == True :
                    print(f'File successfully written to {path}')
            except:
                if os.access(path, os.W_OK) == False:
                    raise ValueError(f"No write permissions for the file : {path}. Verify that the file isn't used by another program")
                else:
                    raise ValueError(f"Could not access the file : {path}")

        elif os.path.isfile(path):
            raise ValueError(f"File already exists : {path}. Try overwite = True.")
        else :
            try: 
                with open(path, 'w') as file:
                    for obj in l:
                        file.write("%s\n" % obj)
                    if verbose == True :
                        print(f'File successfully written to {path}')
            except:
                raise ValueError(f"Could not write on file : {path}")
    else :
        raise ValueError(f"Parameter l is not a list")
		
# rk.read_txt()

def read_txt(path = 'text_file.txt', verbose = False):

#Docstring
	'''
	Reads from a text file, saving the result as a list, where each line is one item.
	
	--------------
	
	path : str, default = 'text_file.txt'
		File path (with file name) you want to read from. Can be any type of file (.txt, .csv...)  
	
	verbose : boolean, default is False
		Prints out a message if the operation was succesful
		
	--------------

	Examples :
	
	var_list = rk.read_txt('./Documents/vars.txt', verbose = True)
	>> File successfully read from ./Documents/vars.txt
	'''
	
	if os.access(path, os.R_OK) == False:
	    raise ValueError(f"No read permissions for the file : {path}. Verify that the file exists")
	else:
	    with open(path) as file:
	        l = file.read().splitlines()
			if verbose == True :
	        		print(f'File successfully read from {path}')
	        return l