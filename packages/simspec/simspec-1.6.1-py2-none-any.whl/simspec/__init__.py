print "This is a non importable package"
print "execute 'simspec' to start SimSpec UI from console"

def main():
    import os
    execfile(os.path.join(os.path.dirname(os.path.realpath(__file__)),'simspec'))