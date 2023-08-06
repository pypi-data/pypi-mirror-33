import sys
import hook
import os
sys.exit(hook.main(sys.argv[1:], os.path.split(os.getcwd())[1]))