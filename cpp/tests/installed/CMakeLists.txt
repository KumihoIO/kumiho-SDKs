cmake_minimum_required(VERSION 3.14)
project(KumihoInstalledConsumer LANGUAGES CXX)

# Use only the installed export and public headers. No source/build include
# directories or direct dependency targets may mask a broken package config.
find_package(kumiho 1.1.0 CONFIG REQUIRED)
add_executable(installed_inventory_probe ../ce_inventory_probe.cpp)
target_link_libraries(installed_inventory_probe PRIVATE kumiho::kumiho)
