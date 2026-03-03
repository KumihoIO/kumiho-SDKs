// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

/// Control-plane discovery helpers.
///
/// See [clientFromDiscovery] for the easiest way to bootstrap a client
/// that auto-discovers the correct data plane for the current user/tenant.
library;

export 'src/discovery.dart'
    show
        DiscoveryEnvVars,
        DiscoveryRecord,
        getDefaultDiscoveryCacheFile,
        discoverTenant,
        clientFromDiscovery;
