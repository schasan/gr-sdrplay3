INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_MSZ msz)

FIND_PATH(
    MSZ_INCLUDE_DIRS
    NAMES msz/api.h
    HINTS $ENV{MSZ_DIR}/include
        ${PC_MSZ_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    MSZ_LIBRARIES
    NAMES gnuradio-msz
    HINTS $ENV{MSZ_DIR}/lib
        ${PC_MSZ_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/mszTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(MSZ DEFAULT_MSG MSZ_LIBRARIES MSZ_INCLUDE_DIRS)
MARK_AS_ADVANCED(MSZ_LIBRARIES MSZ_INCLUDE_DIRS)
