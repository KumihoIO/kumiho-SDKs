Kumiho Go SDK
=============

**Graph-native creative & AI asset management for Go**

Kumiho is the Go client for `Kumiho Cloud <https://kumiho.io>`_, a graph-native
creative and AI asset-management system. Kumiho tracks revisions, relationships,
and lineage **without uploading your files** ("BYO storage") — it stores paths,
metadata, and the dependency graph.

The Go SDK mirrors the Python gold-standard SDK: a low-level ``Client`` that
wraps every gRPC method, plus fluent domain types (``Project``, ``Space``,
``Item``, ``Revision``, ``Artifact``, ``Edge``, ``Bundle``). It has **full
feature parity** with the Python SDK.

Key Features
------------

- **Graph-Native Design**: track asset relationships, dependencies, and lineage
- **Version Control**: immutable revisions with full history and tagging
- **BYO Storage**: files stay on your local / NAS / on-prem storage
- **Full-text fuzzy search & semantic scoring**: ``Search`` and ``ScoreRevisions``
- **Batch fetch**: ``BatchGetRevisions`` for many revisions in one round-trip
- **Event streaming**: ``EventStream`` with cursor resume, consumer groups, and
  ``GetEventCapabilities``
- **Idiomatic Go**: ``context.Context`` throughout, typed errors, no globals

Installation
------------

.. code-block:: bash

   go get github.com/KumihoIO/kumiho-SDKs/go

Quick Start
-----------

.. code-block:: go

   ctx := context.Background()
   client, err := kumiho.Connect(ctx, "https://us-central.kumiho.cloud")
   if err != nil {
       log.Fatal(err)
   }
   defer client.Close()

   project, _ := client.CreateProject(ctx, "my-vfx-project", "VFX assets")
   space, _ := project.CreateSpace(ctx, "characters", "")
   item, _ := space.CreateItem(ctx, "hero", "model")
   rev, _ := item.CreateRevision(ctx, nil, 0)
   rev.CreateArtifact(ctx, "mesh", "/assets/hero.fbx", nil)
   rev.Tag(ctx, "approved")

The full, generated API reference is in :doc:`api`.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   getting-started
   api

----

For the other Kumiho SDKs see `docs.kumiho.io <https://docs.kumiho.io>`_
(Python, C++, Dart, Rust). The canonical Go package reference is also available
on `pkg.go.dev <https://pkg.go.dev/github.com/KumihoIO/kumiho-SDKs/go>`_.
