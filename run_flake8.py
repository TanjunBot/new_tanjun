import sys
import subprocess

# Increase the recursion limit
sys.setrecursionlimit(1000)  # You can set this to a higher value if needed

# Run Flake8 with the specified arguments
subprocess.run([
    'flake8',
    '.',
    '--count',
    '--select=E9,F63,F7,F82',
    '--show-source',
    '--statistics',
])

subprocess.run([
    'flake8',
    '.',
    '--count',
    '--exit-zero',
    '--max-complexity=20',
    '--max-line-length=127',
    '--statistics',
])
