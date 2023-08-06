#!/usr/bin/python3

"""This modules supports building CMake projects."""

import devpipeline_cmake.cmake


def make_cmake(current_configuration, common_wrapper):
    """
    Construct a builder that works with CMake.

    Arguments
    current_configuration - configuration for the current target
    common_wrapper - a function to provide integration with built-in
                     functionality
    """
    return devpipeline_cmake.cmake._make_cmake(current_configuration,
                                               common_wrapper)


_CMAKE_TOOL = (make_cmake, "CMake build system generator.")
