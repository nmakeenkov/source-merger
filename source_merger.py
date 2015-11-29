import argparse
import sys
from os import listdir
from os.path import isfile
from os.path import join as join_path


def get_files():
    _path_to_file = {}
    queue = ["."]
    while len(queue) > 0:
        current_path = queue.pop(0)
        files = listdir(current_path)
        for i in files:
            if isfile(join_path(current_path, i)):
                _path_to_file[i] = join_path(current_path, i)
            else:
                queue.append(join_path(current_path, i))
    return _path_to_file


def print_file(_file_name, _path_to_file, _output, _defines):
    try:
        path_to_current_file = _path_to_file[_file_name]
    except KeyError:
        path_to_current_file = _file_name

    try:
        file_lines = open(path_to_current_file, "r").readlines()
    except IOError:
        return False

    print >> _output, "\n\n // Start of %s\n\n" % _file_name,

    if_stack = [True]
    multi_line_comment = False

    for current_line in file_lines:
        if multi_line_comment:
            if current_line.find("*/") != -1:
                multi_line_comment = False
                current_line = current_line[current_line.find("*/") + len("*/"):len(current_line)]
            else:
                continue

        if current_line.find("//") != -1:
            current_line = current_line[0:current_line.find("//")]

        while current_line.find("/*") != -1:
            if current_line.find("*/") != -1:
                current_line = current_line[0:current_line.find("/*")] + " " + current_line[current_line.find("*/") + len("*/"):len(current_line)]
                multi_line_comment = False
            else:
                current_line = current_line[0:current_line.find("/*")]
                multi_line_comment = True

        if current_line.find("//") != -1:
            current_line = current_line[0:current_line.find("//")]

        command = current_line.split()
        if len(command) > 0:
            if command[0] == "#endif":
                if_stack.pop()
                continue

        if not if_stack[len(if_stack) - 1]:
            continue

        if len(command) > 1:
            if command[0] == "#ifndef":
                if_stack.append(not (command[1] in _defines))
                continue
            if command[0] == "#ifdef":
                if_stack.append(command[1] in _defines)
                continue
            if command[0] == "#define":
                _defines.append(command[1])
            if command[0] == "#undef":
                _defines.remove(command[1])

        if current_line.find("#include") != -1:
            index = current_line.find("#include")
            print >> _output, current_line[0:index]
            index += len("#include")
            while current_line[index] != "\"" and current_line[index] != "<":
                index += 1
            included_file_name = ""
            index += 1
            while current_line[index] != "\"" and current_line[index] != ">":
                included_file_name += current_line[index]
                index += 1
            if not print_file(included_file_name, _path_to_file, _output, _defines):
                print >> _output, current_line[current_line.find("#include"):len(current_line)],
            else:
                print >> _output, current_line[index + 1:len(current_line)],
            continue

        print >> _output, "%s" % current_line,

    print >> _output, "\n\n // End of %s\n\n" % _file_name,
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a CPP file from 2 or more "
        + "source files : useful to send your solution "
        + "to testing system")

    parser.add_argument("--outfile", "-o",
                        help="file the result to be written to")
    parser.add_argument("source", nargs="*")

    args = parser.parse_args()

    if args.outfile is None:
        output = sys.stdout
    else:
        output = open(args.outfile, "w")

    path_to_file = get_files()
    defines = []
    for source_file in args.source:
        print_file(source_file, path_to_file, output, defines)