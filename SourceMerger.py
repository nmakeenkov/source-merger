import argparse
import sys


def print_file(filename, output, defined):
    try:
        read = open(filename, "r").readlines()
    except IOError:
        return False

    print >> output, "\n\n // Start of %s\n\n" % filename,

    if_stack = [True]
    multiline_comment = False;

    for cur in read:
        if multiline_comment:
            if cur.find("*/") != -1:
                multiline_comment = False
                cur = cur[cur.find("*/") + len("*/"):len(cur)]
            else:
                continue

        if cur.find("//") != -1:
            cur = cur[0:cur.find("//")]

        while cur.find("/*") != -1:
            if cur.find("*/") != -1:
                cur = cur[0:cur.find("/*")] + " " + cur[cur.find("*/") + len("*/"):len(cur)]
                multiline_comment = False
            else:
                cur = cur[0:cur.find("/*")]
                multiline_comment = True

        if cur.find("//") != -1:
            cur = cur[0:cur.find("//")]

        cmd = cur.split()
        if len(cmd) > 0:
            if cmd[0] == "#endif":
                if_stack.pop()
                continue

        if not if_stack[len(if_stack) - 1]:
            continue

        if len(cmd) > 1:
            if cmd[0] == "#ifndef":
                if_stack.append(not (cmd[1] in defined))
                continue
            if cmd[0] == "#ifdef":
                if_stack.append(cmd[1] in defined)
                continue
            if cmd[0] == "#define":
                defined.append(cmd[1])
            if cmd[0] == "#undef":
                defined.remove(cmd[1])

        if cur.find("#include") != -1:
            ind = cur.find("#include")
            print >> output, cur[0:ind]
            ind += len("#include")
            while cur[ind] != "\"" and cur[ind] != "<":
                ind += 1
            fn = ""
            ind += 1
            while cur[ind] != "\"" and cur[ind] != ">":
                fn += cur[ind]
                ind += 1
            if not print_file(fn, output, defined):
                print >> output, cur[cur.find("#include"):len(cur)],
            else:
                print >> output, cur[ind + 1:len(cur)],
            continue

        print >> output, "%s" % cur,

    print >> output, "\n\n // End of %s\n\n" % filename,
    return True


parser = argparse.ArgumentParser(
    description="Creates a CPP file from 2 or more "
    + "source files : useful to send your solution "
    + "to testing system")

parser.add_argument("--outfile", "-o",
                    help="file the result to be wrote to")
parser.add_argument("source", nargs="*")

args = parser.parse_args()

if args.outfile is None:
    out = sys.stdout
else:
    out = open(args.outfile, "w")

defined = []
for s in args.source:
    print_file(s, out, defined)