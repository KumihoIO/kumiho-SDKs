cmake_minimum_required(VERSION 3.14)
project(KumihoCpp VERSION 1.0.0 LANGUAGES CXX)

# --- Options ---
option(KUMIHO_BUILD_TESTS "Build unit tests" ON)
option(KUMIHO_BUILD_INTEGRATION_TESTS "Build integration tests" ON)
option(KUMIHO_BUILD_EXAMPLES "Build example applications" ON)
option(KUMIHO_BUILD_DOCS "Build API documentation" OFF)
option(KUMIHO_INSTALL "Generate install target" ON)

# --- Add this block to suppress the warning on MSVC ---
if(MSVC)
    add_compile_options(/wd4267)
endif()

# --- gRPC and Protobuf setup ---
find_package(gRPC CONFIG REQUIRED)
find_package(Protobuf CONFIG REQUIRED)
find_package(CURL REQUIRED)

# --- Manually find the gRPC C++ plugin ---
if(DEFINED GRPC_CPP_PLUGIN)
    # Use the provided path
    set(GRPC_CPP_PLUGIN "${GRPC_CPP_PLUGIN}")
    if(NOT EXISTS "${GRPC_CPP_PLUGIN}")
        message(FATAL_ERROR "GRPC_CPP_PLUGIN path does not exist: ${GRPC_CPP_PLUGIN}")
    endif()
else()
    find_program(
        GRPC_CPP_PLUGIN
        NAMES grpc_cpp_plugin.exe
        HINTS "${CMAKE_TOOLCHAIN_FILE}/../../installed/x64-windows/tools/grpc"
    )
    if(NOT GRPC_CPP_PLUGIN)
        message(FATAL_ERROR "Could not find grpc_cpp_plugin.exe. Check vcpkg installation.")
    endif()
endif()
message(STATUS "Found gRPC C++ plugin: ${GRPC_CPP_PLUGIN}")

set(PROTO_FILE ${CMAKE_CURRENT_SOURCE_DIR}/proto/kumiho.proto)
get_filename_component(PROTO_FILENAME ${PROTO_FILE} NAME_WE)

set(PROTO_SRCS ${CMAKE_CURRENT_BINARY_DIR}/${PROTO_FILENAME}.pb.cc)
set(PROTO_HDRS ${CMAKE_CURRENT_BINARY_DIR}/${PROTO_FILENAME}.pb.h)
set(GRPC_SRCS ${CMAKE_CURRENT_BINARY_DIR}/${PROTO_FILENAME}.grpc.pb.cc)
set(GRPC_HDRS ${CMAKE_CURRENT_BINARY_DIR}/${PROTO_FILENAME}.grpc.pb.h)

add_custom_command(
    OUTPUT ${PROTO_SRCS} ${PROTO_HDRS} ${GRPC_SRCS} ${GRPC_HDRS}
    COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_CURRENT_BINARY_DIR}
    COMMAND ${Protobuf_PROTOC_EXECUTABLE}
        --grpc_out=${CMAKE_CURRENT_BINARY_DIR}
        --cpp_out=${CMAKE_CURRENT_BINARY_DIR}
        -I${CMAKE_CURRENT_SOURCE_DIR}/proto
        --plugin=protoc-gen-grpc=${GRPC_CPP_PLUGIN}
        ${PROTO_FILE}
    DEPENDS ${PROTO_FILE}
)

add_library(protobuf_grpc_lib ${PROTO_SRCS} ${GRPC_SRCS})
target_link_libraries(protobuf_grpc_lib PRIVATE gRPC::grpc++ protobuf::libprotobuf)

# --- Kumiho Client Library (Modular Design) ---
add_library(kumiho
    src/client.cpp
    src/kref.cpp
    src/edge.cpp
    src/event.cpp
    src/space.cpp
    src/item.cpp
    src/revision.cpp
    src/artifact.cpp
    src/project.cpp
    src/bundle.cpp
    src/discovery.cpp
    src/token_loader.cpp
)

target_include_directories(kumiho PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include/kumiho>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

# C++17 required for std::optional, std::any, structured bindings
target_compile_features(kumiho PUBLIC cxx_std_17)

target_link_libraries(kumiho PUBLIC
    protobuf_grpc_lib
    gRPC::grpc++
    protobuf::libprotobuf
    CURL::libcurl
)

# --- Event Listener Executable ---
add_executable(kumiho_listener
    app/kumiho_listener.cpp
)

target_link_libraries(kumiho_listener PRIVATE
    kumiho
)

# --- Tests ---
if(KUMIHO_BUILD_TESTS)
    # Required for CTest/ctest integration
    include(CTest)
    enable_testing()

    find_package(GTest REQUIRED)
    include(GoogleTest)

    # API Tests
    add_executable(kumiho_tests
        tests/test_api.cpp
    )
    target_link_libraries(kumiho_tests PRIVATE
        kumiho
        GTest::gtest
        GTest::gmock
        GTest::gtest_main
    )
    gtest_discover_tests(kumiho_tests
        PROPERTIES
            LABELS "unit"
    )

    # Live API Integration Tests (requires running server + auth)
    if(KUMIHO_BUILD_INTEGRATION_TESTS)
        add_executable(kumiho_api_integration_tests
            tests/integration/test_api_live.cpp
        )
        target_link_libraries(kumiho_api_integration_tests PRIVATE
            kumiho
            GTest::gtest
            GTest::gmock
            GTest::gtest_main
        )
        gtest_discover_tests(kumiho_api_integration_tests
            PROPERTIES
                LABELS "integration"
        )
    endif()

    # Streaming Tests
    add_executable(kumiho_streaming_tests
        tests/test_streaming.cpp
    )
    target_link_libraries(kumiho_streaming_tests PRIVATE
        kumiho
        GTest::gtest
        GTest::gmock
        GTest::gtest_main
    )
    gtest_discover_tests(kumiho_streaming_tests
        PROPERTIES
            LABELS "integration"
    )

    # Kref Tests
    add_executable(kumiho_kref_tests
        tests/test_kref.cpp
    )
    target_link_libraries(kumiho_kref_tests PRIVATE
        kumiho
        GTest::gtest
        GTest::gtest_main
    )
    gtest_discover_tests(kumiho_kref_tests
        PROPERTIES
            LABELS "unit"
    )

    # Types Tests
    add_executable(kumiho_types_tests
        tests/test_types.cpp
    )
    target_link_libraries(kumiho_types_tests PRIVATE
        kumiho
        GTest::gtest
        GTest::gtest_main
    )
    gtest_discover_tests(kumiho_types_tests
        PROPERTIES
            LABELS "unit"
    )

    # Token Loader Tests
    add_executable(kumiho_token_tests
        tests/test_token_loader.cpp
    )
    target_link_libraries(kumiho_token_tests PRIVATE
        kumiho
        GTest::gtest
        GTest::gtest_main
    )
    gtest_discover_tests(kumiho_token_tests
        PROPERTIES
            LABELS "unit"
    )

    # Discovery Tests
    add_executable(kumiho_discovery_tests
        tests/test_discovery.cpp
    )
    target_link_libraries(kumiho_discovery_tests PRIVATE
        kumiho
        GTest::gtest
        GTest::gtest_main
    )
    gtest_discover_tests(kumiho_discovery_tests
        PROPERTIES
            LABELS "unit"
    )

    # --- Integration Tests ---
    if(KUMIHO_BUILD_INTEGRATION_TESTS)
        # Workflow Integration Tests
        add_executable(kumiho_workflow_integration_tests
            tests/integration/test_workflow.cpp
        )
        target_link_libraries(kumiho_workflow_integration_tests PRIVATE
            kumiho
            GTest::gtest
            GTest::gtest_main
        )
        gtest_discover_tests(kumiho_workflow_integration_tests
            PROPERTIES
                LABELS "integration"
        )

        # Discovery Integration Tests
        add_executable(kumiho_discovery_integration_tests
            tests/integration/test_discovery_integration.cpp
        )
        target_link_libraries(kumiho_discovery_integration_tests PRIVATE
            kumiho
            GTest::gtest
            GTest::gtest_main
        )
        gtest_discover_tests(kumiho_discovery_integration_tests
            PROPERTIES
                LABELS "integration"
        )
    endif()

    # --- Custom test targets ---
    # Note: Some legacy tests in the unit binaries hit a live server (KumihoApiTest.*).
    # Exclude them by default for the unit target.
    add_custom_target(run_unit_tests
        COMMAND ${CMAKE_CTEST_COMMAND} -C $<CONFIG> --output-on-failure -LE integration
        DEPENDS kumiho_tests kumiho_streaming_tests kumiho_kref_tests kumiho_types_tests kumiho_token_tests kumiho_discovery_tests
        COMMENT "Running unit tests..."
    )

    add_custom_target(run_integration_tests
        COMMAND ${CMAKE_COMMAND} -E env KUMIHO_INTEGRATION_TEST=1 ${CMAKE_CTEST_COMMAND} -C $<CONFIG> --output-on-failure -L integration
        DEPENDS kumiho_workflow_integration_tests kumiho_discovery_integration_tests kumiho_api_integration_tests
        COMMENT "Running integration tests..."
    )
endif()

# --- Installation ---
install(TARGETS kumiho_listener
    RUNTIME DESTINATION ${CMAKE_SOURCE_DIR}/../../apps/cpp
)

# Install required DLLs for Windows
if(WIN32)
    install(FILES
        "g:/git/vcpkg/installed/x64-windows/bin/libprotobuf.dll"
        "g:/git/vcpkg/installed/x64-windows/bin/abseil_dll.dll"
        "g:/git/vcpkg/installed/x64-windows/bin/cares.dll"
        "g:/git/vcpkg/installed/x64-windows/bin/zlib1.dll"
        "g:/git/vcpkg/installed/x64-windows/bin/re2.dll"
        "g:/git/vcpkg/installed/x64-windows/bin/libcrypto-3-x64.dll"
        "g:/git/vcpkg/installed/x64-windows/bin/libssl-3-x64.dll"
        DESTINATION ${CMAKE_SOURCE_DIR}/../../apps/cpp
    )
endif()

# --- Library Installation (for find_package support) ---
if(KUMIHO_INSTALL)
    include(GNUInstallDirs)
    include(CMakePackageConfigHelpers)

    # Install library
    install(TARGETS kumiho protobuf_grpc_lib
        EXPORT kumiho-targets
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    )

    # Install headers
    install(DIRECTORY include/kumiho
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
        FILES_MATCHING PATTERN "*.hpp" PATTERN "*.h"
    )

    # Install generated protobuf headers
    install(FILES
        ${CMAKE_CURRENT_BINARY_DIR}/kumiho.pb.h
        ${CMAKE_CURRENT_BINARY_DIR}/kumiho.grpc.pb.h
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/kumiho
    )

    # Export targets
    install(EXPORT kumiho-targets
        FILE kumiho-targets.cmake
        NAMESPACE kumiho::
        DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/kumiho
    )

    # Create config file
    set(INCLUDE_INSTALL_DIR ${CMAKE_INSTALL_INCLUDEDIR})
    configure_package_config_file(
        ${CMAKE_CURRENT_SOURCE_DIR}/cmake/kumiho-config.cmake.in
        ${CMAKE_CURRENT_BINARY_DIR}/kumiho-config.cmake
        INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/kumiho
        PATH_VARS INCLUDE_INSTALL_DIR
    )

    # Create version file
    write_basic_package_version_file(
        ${CMAKE_CURRENT_BINARY_DIR}/kumiho-config-version.cmake
        VERSION ${PROJECT_VERSION}
        COMPATIBILITY SameMajorVersion
    )

    # Install config files
    install(FILES
        ${CMAKE_CURRENT_BINARY_DIR}/kumiho-config.cmake
        ${CMAKE_CURRENT_BINARY_DIR}/kumiho-config-version.cmake
        DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/kumiho
    )
endif()

# --- Documentation ---
if(KUMIHO_BUILD_DOCS)
    find_package(Doxygen)
    if(DOXYGEN_FOUND)
        add_custom_target(docs
            COMMAND ${DOXYGEN_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/Doxyfile
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
            COMMENT "Generating API documentation with Doxygen..."
            VERBATIM
        )
    else()
        message(WARNING "Doxygen not found. Documentation target will not be available.")
    endif()
endif()

# --- Summary ---
message(STATUS "")
message(STATUS "=== Kumiho C++ SDK Configuration ===")
message(STATUS "Version:              ${PROJECT_VERSION}")
message(STATUS "Build type:           ${CMAKE_BUILD_TYPE}")
message(STATUS "Build tests:          ${KUMIHO_BUILD_TESTS}")
message(STATUS "Build integration:    ${KUMIHO_BUILD_INTEGRATION_TESTS}")
message(STATUS "Build examples:       ${KUMIHO_BUILD_EXAMPLES}")
message(STATUS "Build docs:           ${KUMIHO_BUILD_DOCS}")
message(STATUS "Install:              ${KUMIHO_INSTALL}")
message(STATUS "=====================================")
message(STATUS "")