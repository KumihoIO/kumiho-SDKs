/**
 * @file error.hpp
 * @brief Exception hierarchy for the Kumiho C++ SDK.
 *
 * This header defines all exception types used throughout the Kumiho library,
 * providing structured error handling for different failure scenarios.
 */

#pragma once

#include <stdexcept>
#include <string>

namespace kumiho {
namespace api {

/**
 * @brief Base exception for all Kumiho errors.
 *
 * All Kumiho-specific exceptions inherit from this class, allowing
 * catch blocks to handle all Kumiho errors uniformly.
 */
class KumihoError : public std::runtime_error {
public:
    explicit KumihoError(const std::string& message)
        : std::runtime_error(message) {}
};

/**
 * @brief Exception for gRPC communication failures.
 *
 * Thrown when an RPC call fails due to network issues, server errors,
 * or other gRPC-level problems.
 */
class RpcError : public KumihoError {
public:
    explicit RpcError(const std::string& message, int code = 0)
        : KumihoError(message), code_(code) {}

    /**
     * @brief Get the gRPC status code.
     * @return The gRPC status code (0 = OK, see grpc::StatusCode).
     */
    int code() const noexcept { return code_; }

private:
    int code_;
};

/**
 * @brief Exception for NOT_FOUND errors.
 *
 * Thrown when a requested entity (group, product, version, etc.)
 * does not exist.
 */
class NotFoundError : public KumihoError {
public:
    explicit NotFoundError(const std::string& message)
        : KumihoError(message) {}
};

/**
 * @brief Exception for project limit exceeded.
 *
 * Thrown when attempting to create a project but the tenant's
 * project limit has been reached (RESOURCE_EXHAUSTED).
 */
class ProjectLimitError : public KumihoError {
public:
    explicit ProjectLimitError(const std::string& message)
        : KumihoError(message) {}
};

/**
 * @brief Exception for input validation failures.
 *
 * Thrown when user-provided input fails validation (e.g., invalid
 * kref format, invalid time format, reserved product type).
 */
class ValidationError : public KumihoError {
public:
    explicit ValidationError(const std::string& message)
        : KumihoError(message) {}
};

/**
 * @brief Exception for Kref URI validation failures.
 *
 * Thrown when a Kref string does not match the expected format.
 */
class KrefValidationError : public ValidationError {
public:
    explicit KrefValidationError(const std::string& message)
        : ValidationError(message) {}
};

/**
 * @brief Exception for link type validation failures.
 *
 * Thrown when a link type does not match the required format
 * (uppercase, alphanumeric with underscores, 1-50 chars).
 */
class LinkTypeValidationError : public ValidationError {
public:
    explicit LinkTypeValidationError(const std::string& message)
        : ValidationError(message) {}
};

/**
 * @brief Exception for reserved product type violations.
 *
 * Thrown when attempting to create a product with a reserved type
 * (e.g., "collection") using createProduct() instead of the
 * dedicated method.
 */
class ReservedProductTypeError : public ValidationError {
public:
    explicit ReservedProductTypeError(const std::string& message)
        : ValidationError(message) {}
};

/**
 * @brief Exception for discovery failures.
 *
 * Thrown when the discovery endpoint cannot be reached or returns
 * an unexpected response.
 */
class DiscoveryError : public KumihoError {
public:
    explicit DiscoveryError(const std::string& message)
        : KumihoError(message) {}
};

/**
 * @brief Exception for authentication failures.
 *
 * Thrown when authentication fails or credentials are invalid.
 */
class AuthenticationError : public KumihoError {
public:
    explicit AuthenticationError(const std::string& message)
        : KumihoError(message) {}
};

} // namespace api
} // namespace kumiho
