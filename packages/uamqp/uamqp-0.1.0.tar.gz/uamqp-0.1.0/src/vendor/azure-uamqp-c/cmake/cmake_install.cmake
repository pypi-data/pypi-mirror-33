# Install script for directory: /data/azure-uamqp-c

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
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/azure_uamqp_c" TYPE FILE FILES
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/amqp_definitions.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/amqp_frame_codec.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/amqp_management.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/amqp_types.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/amqpvalue.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/amqpvalue_to_string.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/async_operation.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/cbs.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/connection.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/frame_codec.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/header_detect_io.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/link.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/message.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/message_receiver.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/message_sender.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/messaging.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/sasl_anonymous.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/sasl_frame_codec.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/sasl_mechanism.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/sasl_server_mechanism.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/sasl_mssbcbs.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/sasl_plain.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/saslclientio.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/sasl_server_io.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/server_protocol_io.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/session.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/socket_listener.h"
    "/data/azure-uamqp-c/./inc/azure_uamqp_c/uamqp.h"
    )
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "/data/azure-uamqp-c/cmake/libuamqp.a")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("/data/azure-uamqp-c/cmake/deps/azure-c-shared-utility/cmake_install.cmake")
  include("/data/azure-uamqp-c/cmake/samples/cmake_install.cmake")

endif()

if(CMAKE_INSTALL_COMPONENT)
  set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
file(WRITE "/data/azure-uamqp-c/cmake/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
