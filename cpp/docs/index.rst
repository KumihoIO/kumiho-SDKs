.. Kumiho C++ SDK documentation master file

Kumiho C++ SDK
==============

**Graph-native creative & AI asset management for C++**

Kumiho is a C++ SDK for `Kumiho Cloud <https://kumiho.io>`_, a graph-native
creative and AI asset management platform designed for VFX, animation, and
AI-driven workflows.

The C++ SDK (version 1.0.0) ships from the ``cpp/`` directory of the
`KumihoIO/kumiho-SDKs <https://github.com/KumihoIO/kumiho-SDKs>`_ monorepo and
has full feature parity with the Python SDK.

Features
--------

* **Graph-native model** — projects, spaces, items, revisions, artifacts,
  edges, and bundles.
* **Full-text fuzzy search** — ``search()`` returns items ranked by a
  relevance score.
* **Semantic revision scoring** — ``scoreRevisions()`` ranks revisions
  against a query using server-side embeddings.
* **Batch revision fetch** — ``batchGetRevisions()`` resolves many
  revisions (by revision kref, or by item kref + tag) in a single call.
* **By-kref accessors** — ``getItemFromRevision()``,
  ``getArtifactByKref()``, and ``getBundleByKref()``.
* **Event streaming** — ``eventStream()`` with cursor resume, consumer
  groups, ``from_beginning`` replay, and timeout; ``getEventCapabilities()``
  reports the tenant tier's streaming limits.
* **Graph traversal** — dependency tracking, shortest-path, and impact analysis.

Installation
------------

The SDK is built from source from the ``cpp/`` subdirectory of the monorepo
(vcpkg recommended for dependencies):

.. code-block:: bash

   git clone https://github.com/KumihoIO/kumiho-SDKs.git
   cd kumiho-SDKs/cpp
   cmake -B build -DCMAKE_TOOLCHAIN_FILE=[vcpkg root]/scripts/buildsystems/vcpkg.cmake
   cmake --build build --config Release

See ``cpp/README.md`` for the full build matrix (Windows / Linux / macOS) and
vcpkg manifest details.

Quickstart
----------

.. code-block:: cpp

   #include <kumiho/kumiho.hpp>

   using namespace kumiho::api;

   auto client = Client::createFromEnv();

   // Full-text fuzzy search, ranked by relevance score.
   for (const auto& hit : client->search("hero model")) {
       std::cout << hit.item->getKref().uri() << " (" << hit.score << ")\n";
   }

   // Semantic scoring of specific revisions via server-side embeddings.
   auto scored = client->scoreRevisions("battle damage", {revKref});

   // Fetch many revisions in one round-trip.
   auto [found, missing] = client->batchGetRevisions({revKrefA, revKrefB});

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
