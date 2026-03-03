Usage Guide
===========

Two Layers of API
-----------------

* **High-level models** in ``package:kumiho/models.dart`` mirror the Python SDK and offer a fluent interface for creating spaces, items, revisions, artifacts, and bundles.
* **gRPC wrapper mixins** on ``KumihoClient`` (``ProjectApi``, ``SpaceApi``, etc.) expose the raw request/response objects generated from ``kumiho.proto``.

Most applications start with the high-level models for readability and only drop down to the gRPC layer for specialized workflows.

Krefs
-----

Every object in Kumiho is addressable by a URI-style ``kref`` (for example ``kref:///project/space/item``). API calls accept either human-readable paths or krefs, and responses include a kref you can store to revisit the object later or to attach relationships.

Working with Projects
---------------------

Projects are the root namespace for everything in Kumiho.

.. code-block:: dart

   final client = KumihoClient(host: 'localhost', port: 50051);
   final project = await client.createProject('film-2025', description: 'VFX assets');

   // Update settings or deprecate the project
   await project.update(description: 'Updated description');
   await project.setPublic(true);
   await project.delete();

   // List projects using the low-level API
   final projects = await client.getProjects();

Spaces: Organizing Assets
-------------------------

Spaces form a hierarchical folder structure inside a project. You can nest spaces and attach metadata to them.

.. code-block:: dart

   final assets = await project.createSpace('assets');
   final characters = await project.createSpace('characters', parentPath: '/film-2025/assets');

   final heroes = await project.getSpace('assets/characters');
   final children = await heroes.getChildSpaces(recursive: true);

   await client.updateSpaceMetadata(heroes.kref, {'status': 'active', 'owner': 'asset-team'});

Items and Revisions
-------------------

Items represent versioned assets such as models, textures, or workflows. Each item holds one or more revisions.

.. code-block:: dart

   final item = await project.createItem('hero', 'model', parentPath: '/film-2025/assets/characters');
   final revision = await item.createRevision();

   // Add artifacts that point to storage locations you control
   await revision.createArtifact('mesh', '/mnt/assets/hero.fbx');
   await revision.createArtifact('textures', 's3://bucket/hero/textures.tar');

   // Link revisions with edges to express dependencies
   final rig = await project.createItem('hero-rig', 'rig');
   final rigRevision = await rig.createRevision();
   await revision.addEdge(rigRevision, EdgeType.dependsOn);

Bundles
-------

Bundles aggregate other items or revisions to represent releases or delivery packages.

.. code-block:: dart

   final bundle = await project.createBundle('release-v1', metadata: {'channel': 'beta'});
   await bundle.addMember(item.kref);
   await bundle.addMember(rigRevision.kref);

Events and Tenants
------------------

Subscribe to event streams to monitor changes, or query tenant metadata when running inside a multi-tenant deployment.

.. code-block:: dart

   final stream = client.subscribeEvents();
   await for (final event in stream) {
     print('Event: ${event.kind} on ${event.kref}');
   }

   final tenantInfo = await client.getTenant();
   print('Tenant: ${tenantInfo.name}');
