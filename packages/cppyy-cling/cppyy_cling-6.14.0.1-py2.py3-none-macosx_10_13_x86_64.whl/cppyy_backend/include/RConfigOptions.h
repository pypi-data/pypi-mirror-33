#ifndef ROOT_RConfigOptions
#define ROOT_RConfigOptions

#define R__CONFIGUREOPTIONS   "LZ4_INCLUDE_DIR=/opt/local/include LZ4_LIBRARY=/opt/local/lib/liblz4.dylib LZMA_INCLUDE_DIR=/opt/local/include LZMA_LIBRARY=/usr/lib/liblzma.dylib PCRE_INCLUDE_DIR=/opt/local/include PCRE_PCREPOSIX_LIBRARY=/usr/lib/libpcreposix.dylib PCRE_PCRE_LIBRARY=/usr/lib/libpcre.dylib ZLIB_INCLUDE_DIR=/usr/include ZLIB_LIBRARY_RELEASE=/usr/lib/libz.dylib xxHash_INCLUDE_DIR=/Users/wlav/wheelie/cppyy-backend/cling/src/builtins/xxhash xxHash_INCLUDE_DIRS=/Users/wlav/wheelie/cppyy-backend/cling/src/builtins/xxhash xxHash_LIBRARIES=xxHash::xxHash xxHash_LIBRARY=$<TARGET_FILE:xxhash> "
#define R__CONFIGUREFEATURES  " builtin_llvm builtin_clang builtin_xxhash cling cxx14 explicitlink libcxx thread"

#endif
