__ver_major__ = 0
__ver_minor__ = 2
__ver_patch__ = 5
__ver_tuple__ = (__ver_major__, __ver_minor__, __ver_patch__)
__version__ = "%d.%d.%d" % __ver_tuple__

from .main import analyze_segments, acoustic_similarity_directories, acoustic_similarity_mapping, \
    acoustic_similarity_directory, analyze_long_file
