# Let local_compiler be None in order to use the default compiler
local_compiler = None
local_linker = local_compiler
extra_compile_args = []
extra_link_args = []
local_link_shared = []

# # Example: Explicitly use gcc
# #
# # local_compiler = 'gcc'
# extra_compile_args = ['-fPIC',
#                       '-Ofast',
#                       '-march=native',
#                       '-std=c99']

# local_linker = local_compiler
# local_link_shared = ['-shared']
# extra_link_args = []


# # Example: Use icc instead of the default compiler
# #
# local_compiler = 'icc'
# extra_compile_args = ['-openmp', '-xHOST', '-O3',
#                       '-fno-alias', '-fPIC', '-std=c99']

# local_linker = local_compiler
# local_link_shared = ['-shared']
# extra_link_args = ['-openmp']


# # Example: Use pgcc instead of the default compiler
# #
# local_compiler = 'pgcc'
# extra_compile_args = ['-mp=numa', '-O4', '-Msafeptr', '-fPIC', '-c99']

# local_linker = local_compiler
# local_link_shared = ['-shared']
# extra_link_args = ['-mp']


# # Example: Use pgcc to generate GPU-code using OpenACC directives
# #
# local_compiler = 'pgcc'
# extra_compile_args = ['-acc', '-ta=nvidia', '-O4',
#                       '-g', '-Minfo=acc', '-fPIC']

# local_linker = local_compiler
# local_link_shared = ['-shared']
# extra_link_args = ['-acc']
