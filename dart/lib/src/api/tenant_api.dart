// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

import '../base_client.dart';
import '../generated/kumiho.pbgrpc.dart';

/// Tenant API mixin for multi-tenant SaaS features.
///
/// Tenants represent isolated environments in the Kumiho SaaS model.
/// Each authenticated user belongs to a tenant, and all their data
/// is isolated from other tenants.
///
/// ```dart
/// // Get current tenant usage
/// final usage = await client.getTenantUsage();
/// print('Using ${usage.nodeCount} of ${usage.nodeLimit} nodes');
/// ```
mixin TenantApi on KumihoClientBase {
  /// Gets the current tenant's usage statistics.
  ///
  /// Returns the number of nodes (items, revisions, etc.) used
  /// and the tenant's limit. Useful for quota monitoring.
  Future<TenantUsageResponse> getTenantUsage() async {
    final request = GetTenantUsageRequest();
    return stub.getTenantUsage(request, options: callOptions);
  }
}
