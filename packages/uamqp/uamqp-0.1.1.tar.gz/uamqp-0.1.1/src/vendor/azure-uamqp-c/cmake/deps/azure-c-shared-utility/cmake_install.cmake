# Install script for directory: /data/azure-uamqp-c/deps/azure-c-shared-utility

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/azure_c_shared_utility" TYPE FILE FILES
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/agenttime.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/base32.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/base64.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/buffer_.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/connection_string_parser.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/crt_abstractions.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/constmap.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/condition.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/const_defines.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/inc/azure_c_shared_utility/consolelogger.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/doublylinkedlist.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/gballoc.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/gbnetwork.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/gb_stdio.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/gb_time.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/gb_rand.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/hmac.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/hmacsha256.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/http_proxy_io.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/singlylinkedlist.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/lock.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/macro_utils.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/map.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/optimize_size.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/platform.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/refcount.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/sastoken.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/sha-private.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/shared_util_options.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/sha.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/socketio.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/stdint_ce6.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/strings.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/strings_types.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/string_tokenizer.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/string_tokenizer_types.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/tickcounter.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/threadapi.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/xio.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/umock_c_prod.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/uniqueid.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/uuid.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/urlencode.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/vector.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/vector_types.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/vector_types_internal.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/xlogging.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/constbuffer.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/tlsio.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/optionhandler.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./adapters/linux_time.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/wsio.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/uws_client.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/uws_frame_encoder.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/utf8_checker.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/httpapi.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/httpapiex.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/httpapiexsas.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/httpheaders.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/tlsio_openssl.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./inc/azure_c_shared_utility/x509_openssl.h"
    "/data/azure-uamqp-c/deps/azure-c-shared-utility/./pal/linux/refcount_os.h"
    )
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "/data/azure-uamqp-c/cmake/deps/azure-c-shared-utility/libaziotsharedutil.a")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("/data/azure-uamqp-c/cmake/deps/azure-c-shared-utility/samples/cmake_install.cmake")

endif()

