################################################################################
#
#       CMAKE
#
################################################################################

set(_CMAKE_LIBRARIES
    CMakeLib
    cmsys
    ${CMAKE_EXPAT_LIBRARIES}
    ${CMAKE_ZLIB_LIBRARIES}
    ${CMAKE_TAR_LIBRARIES}
    ${CMAKE_COMPRESS_LIBRARIES}
    ${CMAKE_CURL_LIBRARIES}
    ${CMAKE_JSONCPP_LIBRARIES}
    ${CMAKE_LIBUV_LIBRARIES}
    ${CMAKE_LIBRHASH_LIBRARIES}
    ${CMake_KWIML_LIBRARIES}
)
set(_CMAKE_LIBRARY_UTILITIES
    BZIP2 CURL EXPAT FORM JSONCPP LIBARCHIVE LIBLZMA LIBRHASH LIBUV ZLIB)

foreach(_PACKAGE ${_CMAKE_LIBRARY_UTILITIES})
    if(NOT CMAKE_USE_SYSTEM_${_PACKAGE} AND ${_PACKAGE}_LIBRARY)
        list(APPEND _CMAKE_LIBRARIES ${${_PACKAGE}_LIBRARY})
    endif(NOT CMAKE_USE_SYSTEM_${_PACKAGE} AND ${_PACKAGE}_LIBRARY)
endforeach(_PACKAGE ${_CMAKE_LIBRARY_UTILITIES})

list(REMOVE_DUPLICATES _CMAKE_LIBRARIES)

export(TARGETS ${_CMAKE_LIBRARIES}
    FILE ${CMAKE_BINARY_DIR}/CMakeLibBuild.cmake)

set_property(GLOBAL PROPERTY CMAKE_PROJECT_LIBRARIES ${_CMAKE_LIBRARIES})

################################################################################
#
#       CTEST
#
################################################################################

set(_CTEST_LIBRARIES
    CTestLib
    ${CMAKE_CURL_LIBRARIES}
    ${CMAKE_XMLRPC_LIBRARIES}
    #cmsys
    #${CMAKE_EXPAT_LIBRARIES}
    #${CMAKE_ZLIB_LIBRARIES}
    #${CMAKE_TAR_LIBRARIES}
    #${CMAKE_COMPRESS_LIBRARIES}
    #${CMAKE_JSONCPP_LIBRARIES}
    #${CMAKE_LIBUV_LIBRARIES}
    #${CMAKE_LIBRHASH_LIBRARIES}
    #${CMake_KWIML_LIBRARIES}
)

# check if built or using system
set(_CTEST_LIBRARY_UTILITIES
    BZIP2 CURL EXPAT FORM JSONCPP LIBARCHIVE LIBLZMA LIBRHASH LIBUV ZLIB)

# assemble list
foreach(_PACKAGE ${_CTEST_LIBRARY_UTILITIES})
    if(NOT CMAKE_USE_SYSTEM_${_PACKAGE} AND ${_PACKAGE}_LIBRARY)
        list(APPEND _CTEST_LIBRARIES ${${_PACKAGE}_LIBRARY})
    endif(NOT CMAKE_USE_SYSTEM_${_PACKAGE} AND ${_PACKAGE}_LIBRARY)
endforeach(_PACKAGE ${_CTEST_LIBRARY_UTILITIES})

list(REMOVE_DUPLICATES _CTEST_LIBRARIES)

export(TARGETS ${_CTEST_LIBRARIES}
    FILE ${CMAKE_BINARY_DIR}/CTestLibBuild.cmake)

set_property(GLOBAL PROPERTY CTEST_PROJECT_LIBRARIES ${_CTEST_LIBRARIES})

################################################################################
