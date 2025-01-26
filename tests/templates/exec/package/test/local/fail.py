import os
import sys

file_flag = os.path.join(os.environ['TARGET_DIR'], 'invoked-fail')
with open(file_flag, 'ab'):
    os.utime(file_flag, None)

# non-zero return code
sys.exit(1)
