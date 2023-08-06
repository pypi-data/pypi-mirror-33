# Install script for directory: /data/azure-uamqp-c/samples

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

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("/data/azure-uamqp-c/cmake/samples/message_sender_sample/cmake_install.cmake")
  include("/data/azure-uamqp-c/cmake/samples/message_receiver_sample/cmake_install.cmake")
  include("/data/azure-uamqp-c/cmake/samples/mssbcbs_sample/cmake_install.cmake")
  include("/data/azure-uamqp-c/cmake/samples/eh_sender_with_sas_token_sample/cmake_install.cmake")
  include("/data/azure-uamqp-c/cmake/samples/local_client_sample/cmake_install.cmake")
  include("/data/azure-uamqp-c/cmake/samples/websockets_sample/cmake_install.cmake")

endif()

