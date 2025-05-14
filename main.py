#MARK: Libraries
import ast
import argparse

#MARK: Arg parser
parser = argparse.ArgumentParser(description="A program to auto generate changelogs based on a list of files", )




if "-A" in argv:
    auto_mode_enabled = True
else:
    auto_mode_enabled = False
