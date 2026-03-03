Configuration and Operations
============================

Connection Settings
-------------------

``KumihoClient`` accepts either an existing ``ClientChannelBase`` or a host/port pair. Set ``secure: true`` to enable TLS for production deployments, or pass a custom ``ChannelOptions`` instance to tune deadlines and credentials. In local setups you can keep ``secure`` disabled to use plaintext connections.

Call Options and Metadata
-------------------------

Use ``callOptions`` to include the current Bearer token in every request. When you need per-call overrides—such as additional metadata or custom deadlines—use ``mergeOptions`` to combine them with the defaults without losing authentication headers.

Lifecycle
---------

The client owns the gRPC channel unless you supply one yourself. Call ``shutdownAsync`` to close the underlying channel and await completion when your process exits. The non-awaiting ``shutdown`` method is also available for fire-and-forget semantics in short-lived scripts or Flutter background tasks.

Error Handling
--------------

gRPC errors surface as ``GrpcError`` instances. Common scenarios include:

* Invalid project or space names that fail server-side validation.
* Permission failures when the token lacks access to a tenant or project.
* Expired tokens when auto-refresh is disabled.

Handle these errors at the edges of your application and retry after refreshing tokens or adjusting request parameters.
