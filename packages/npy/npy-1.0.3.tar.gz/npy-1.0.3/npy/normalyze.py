"""
Author: ZviWex
"""
import argparse
import sys
import os

def indent(line, depth):
    line = line.strip()
    return ("    " * depth) + line

def opening_statement(line, depth):
    if line[-1] != ":":
        line = line + ":"
    return indent(line, depth)

def branch(line, depth):
    return indent(line[1:], depth)


def _parse(code, is_module):
    depth = 0
    new_code = []
    lined_string = False
    for line_idx in xrange(len(code)):
        if is_module:
            # If this is module configuration, supporting new lined-string format
            code[line_idx] = code[line_idx].replace('"-"-"', '"""')
        
        if '"""' in code[line_idx]:
            lined_string = not lined_string 
        
        if not lined_string:
            # If this is start of block
            if len(code[line_idx]) > 0 and code[line_idx][0] == '{' and line_idx != 0:
                
                # Finding the opening statement in old code
                i = -1
                while new_code[i].strip() == "":
                    i -= 1

                # Finding the opening statement in new code            
                j = -1
                while new_code[j].strip() != new_code[i].strip():
                    j -= 1

                # Fixing opening statement
                new_code[i] = opening_statement(new_code[j], depth)
                
                # Fixing branch line
                line = branch(code[line_idx], depth)
                
                # Adding line
                if line.strip() != "":
                    new_code.append(line)
            
                depth += 1
        
            # If this is end of block
            elif len(code[line_idx]) > 0 and code[line_idx][0] == '}':
                line = branch(code[line_idx], depth)
                if line.strip() != "":
                    new_code.append(line)
                depth -= 1
            
            else:
                new_code.append(indent(code[line_idx], depth))
        else:
            new_code.append(indent(code[line_idx], depth))
            
    return new_code

def parse_file_and_save(file_path, is_module = False):
    if ".npy" not in file_path[-4:]:
        raise(Exception("Error: not npy file"))

    with open(file_path, 'r') as f:
        code = [x.strip() for x in f.read().splitlines()]
    
    code = _parse(code, is_module)
    
    with open(file_path[:-4] + ".py", 'w') as f:
        f.write("\n".join(code))
    


def as_runner(path, is_dir):

        
    path = os.path.abspath(path)
    
    if is_dir:
        for root, _, files in os.walk(path):
            for ffile in files:
                file_path = os.path.join(root, ffile)
                parse_file_and_save(file_path) 
    else:
        parse_file_and_save(path)



def run(code):
    code = [x.strip() for x in code.splitlines()]
    code = _parse(code, True)

    code = "\n".join(code)
    return(code)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Normalyzing Python block and indentation system')
    parser.add_argument('-d', '--is_dir', action='store_true', help="if you want to normalyze a directory")
    parser.add_argument('path', help="file / directory path")
    args =  parser.parse_args()
    as_runner(args.path, args.is_dir)