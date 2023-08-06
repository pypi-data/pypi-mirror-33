import sys,os,site,pdb

if __package__:
    # peforth is imported as a package
    from . import projectk as vm
else:
    # peforth is run from __main__.py
    import projectk as vm

# Let projtct-k know itself
vm.vm = vm

# Get command line, as is
vm.commandline = " ".join(sys.argv[1:])

# panic() when something wrong
def panic(msg,serious=False):
    # defined in project-k kernel peforth.py
    print("\n{}".format(msg))
    if serious:
        c = input("Continue, Debug, or Abort? [C/d/a] ")
        if c in ['D', 'd']:
            pdb.set_trace()
        elif c in ['A', 'a']:
            vm.reset()
    else:
        vm.reset()

vm.panic = panic

# Toggle multiple or single lines by ^D
vm.multiple = False

def readTextFile(pathname):
    f = open(pathname,'r',encoding='utf-8')
    # for line in f:
    s = f.read()
    f.close()
    return s
vm.readTextFile = readTextFile

def writeTextFile(pathname, string):
    f = open(pathname,"wt",encoding='utf-8')
    f.write(string)
    f.close
vm.writeTextFile = writeTextFile

# Get the path of data files is really frustrating. 
# The below method is the only ugly way I have so far:
deli = '\\' if os.name == 'nt' else '/'
path = "something wrong peforth path not found"
for p in sys.path:
    if os.path.isfile(p + deli + 'peforth' + deli + 'version.txt'):
        path = p + deli + 'peforth' + deli
        break
vm.path = path

# Get version code from peforth/version.txt for whl package
# to see the single source of version code.
exec(readTextFile(path + "version.txt"),{},locals())
vm.version = __version__
def greeting():
    print("p e f o r t h    v" + str(vm.version));
    print("source code http://github.com/hcchengithub/peforth");
    print("Type 'peforth.ok()' to enter forth interpreter, 'exit' to come back.\n");
    return vm.version;
vm.greeting = greeting

# Master switch to break ok() and return to python interpreter
vm.exit = False

def ok(prompt='OK ', loc={}, glo={}, cmd=""):
    '''
    Invoke the peforth interpreter.
    An statement: peforth.ok(prompt='OK ', loc=locals(), glo=globals(), cmd="") 
    is like a breakpoint. The prompt indicates which breakpoint it is if there are 
    many. Arguments loc (locals) and glo (globals) along with the prompt are the 
    debuggee's informations that is packed as a tuple (loc,glo,prompt) left on TOS 
    of the FORTH vm when the breakpoint is called. Replace the loc=locals() with
    loc=dict(locals()) to get a snapshot copy instead of a reference, as well as 
    the glo. 'exit' command to stop debugging.
    '''
    if loc or glo: vm.push((loc,glo,prompt))  # parent's data
    while True:
        if cmd == "":                                    #
            if vm.tick('accept') and not vm.multiple:    # Input can be single line (default) or
                vm.execute('accept')                     # multiple lines. Press Ctrl-D to toggle
                cmd = vm.pop().strip()                   # between the two modes. Place a Ctrl-D
            elif vm.tick('<accept>') and vm.multiple:    # before the last <Enter> key to end the
                vm.execute('<accept>')                   # input when in multiple-line mode.
                cmd = vm.pop().strip()                   #
            else:                                        #
                cmd = input("").strip()                  #

        # pass the command line to forth VM
        if cmd == "":
            print(prompt, end="")
            continue
        elif cmd == chr(4):
            vm.multiple = not vm.multiple
            if not vm.multiple: print(prompt, end="")
        else:
            vm.dictate(cmd)
            if vm.multiple: vm.multiple = False # switch back to the normal mode
            print(prompt, end="")
        cmd = ""
        # Master switch vm.exit is a flag of boolean. When it's True
        # then exit to the caller that usually is python interpreter.
        if vm.exit:
            vm.exit = False # Avoid exit immediately when called again
            break
    return(vm) # support function cascade
vm.ok = ok  # invoke REPL from within REPL, I don't know if we need this.

# Aliases that make it easier to access project-k methods and properties
# So we can use peforth.dictate(), peforth.execute(), and peforth.push() directly
# instead of peforth.vm.dictate(), peforth.vm.execute(), and peforth.vm.push().
dictate     = vm.dictate
execute     = vm.execute
push        = vm.push    
debug       = vm.debug
dictionary  = vm.dictionary
ntib        = vm.ntib
pop         = vm.pop
reset       = vm.reset
rpop        = vm.rpop
rstack      = vm.rstack
rtos        = vm.rtos
stack       = vm.stack
tib         = vm.tib
tos         = vm.tos
words       = vm.words

##### Setup peforth magic command %f and %%f for ipython and jupyter notebook ##### 

# How to tell if ipython magic is available? 
#     pdb.set_trace() works fine here even when run from jupyter notebook
#     if 'get_ipython' in globals():  <--- always false 
#     if '__IPYTHON__' in dir(__builtins__):  <--- always false 
#     if '__IPYTHON__' in __builtins__.keys(): <--- previous way, not suitable for ipython -m peforth
#     if 'IPython' in sys.modules.keys(): <--- a candidate never tried
try:
    flag = "InteractiveShell" in str(get_ipython)
except:
    flag = False

if flag:
    from IPython.core.magic import register_line_cell_magic

    # Define peforth magic command, %f.
    @register_line_cell_magic
    def f(line, cell=None):
        if cell is None:
            vm.dictate(line)
        else:
            vm.dictate(cell)
            
    # Register auto '%load_ext peforth' at an ipython session
    def load_ipython_extension(ipython):
        ipython.register_magic_function(f, 'line_cell')  
        # see http://ipython.readthedocs.io/en/stable/api/generated/IPython.core.interactiveshell.html?highlight=register_magic_function

# Run once
if not vm.tick('version'):  # defined in peforth.f 
    vm.dictate(readTextFile(path+'peforth.f'))
    vm.dictate(readTextFile(path+'peforth.selftest'))
    vm.dictate(readTextFile(path+'quit.f'))

##### End of peforth __init__.py #####

