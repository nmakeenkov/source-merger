
# coding: utf-8

# In[30]:

import argparse
import sys
from os import listdir
from os.path import isfile
from os.path import join
from os.path import dirname


# In[31]:

def getNameToPathMap():
    nt_path = {}
    queue = ["."]
    while len(queue) > 0:
        current_path = queue.pop(0)
        files = listdir(current_path)
        for i in files:
            if isfile(join_path(current_path, i)):
                bt_path[i] = join(current_path, i)
            else:
                queue.append(join(current_path, i))
    return nt_path


# In[32]:

def process(filepath, merged):
    if (filepath in merged):
        return ""
    text = ""
    try:
	infile = open(filepath)
    except IOError, err:
        return False
    merged.append(filepath)
    text += "\n\n // Start of %s\n\n" % filepath
    file_lines = infile.readlines()

    for current_line in file_lines:
        index = current_line.find("#include")
        if index == -1:
	    text += current_line
        else:
	    text += current_line[0:index]
	    index += len("#include")
	    while current_line[index] != "\"" and current_line[index] != "<":
	        index += 1
	    included_file_name = ""
	    index += 1
	    while current_line[index] != "\"" and current_line[index] != ">":
	        included_file_name += current_line[index]
	        index += 1
	    included_file_path = join(dirname(filepath) + "/", included_file_name)
	    included_text = process(included_file_path, merged)
	    if (included_text == False):
                index = current_line.find("#include")
	        text += current_line[index:]
	    else:
	        text += included_text + current_line[index + 1:]
    return text


# In[33]:

def merge(filenames):
    merged = []
    text = ""
    for filename in filenames:
        text += process(filename, merged)
    return text


# In[34]:

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a CPP file from 2 or more "
        + "source files : useful to send your solution "
        + "to testing system")
    parser.add_argument("--outfile", "-o",
                        help="file the result to be written to")
    parser.add_argument("sources", nargs="*")

    args = parser.parse_args()

    if args.outfile is None:
        output = sys.stdout
    else:
        output = open(args.outfile, "w")

    sources = ['./' + filename for filename in args.sources]

    merged_text = merge(sources)
    output.write(merged_text)

