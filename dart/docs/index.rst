.. Kumiho Dart SDK documentation master file

Kumiho Dart SDK
===============

**Graph-native creative & AI asset management for Dart/Flutter**

.. image:: https://img.shields.io/badge/pub-v0.2.0-blue.svg
   :target: https://pub.dev/packages/kumiho
   :alt: Pub version

.. image:: https://img.shields.io/badge/dart-%3E%3D3.7.0-blue.svg
   :target: https://dart.dev/
   :alt: Dart versions

.. image:: https://img.shields.io/badge/flutter-compatible-blue.svg
   :target: https://flutter.dev/
   :alt: Flutter compatible

Kumiho is a Dart SDK for `Kumiho Cloud <https://kumiho.io>`_, a graph-native
creative and AI asset management platform designed for VFX, animation, and
AI-driven workflows.

Key Features
------------

- **Graph-Native Design**: Built on Neo4j for tracking asset relationships and lineage
- **Version Control**: Semantic versioning for creative assets with full history
- **AI Lineage Tracking**: Track AI model training data provenance and dependencies
- **BYO Storage**: Files stay on your local/NAS/on-prem storage
- **Multi-Tenant SaaS**: Secure, region-aware multi-tenant architecture
- **Flutter Compatible**: Works seamlessly with Flutter for desktop and mobile apps

Quick Start
-----------

Installation
^^^^^^^^^^^^

Add the SDK to your ``pubspec.yaml``:

.. code-block:: yaml

   dependencies:
     kumiho:
       git:
         url: https://github.com/kumihoclouds/kumiho-dart.git

Then fetch dependencies:

.. code-block:: bash

   dart pub get

Authentication
^^^^^^^^^^^^^^

First, authenticate with Kumiho Cloud using the CLI:

.. code-block:: bash

   kumiho-auth login

This will prompt for your credentials and cache them for the SDK.

Basic Usage
^^^^^^^^^^^

.. code-block:: dart

   import 'package:kumiho/kumiho.dart';

   Future<void> main() async {
     final client = KumihoClient(
       host: 'localhost',
       port: 50051,
     );

     try {
       // Create a new project
       final project = await client.createProject('my-vfx-project');

       // Create a space for characters
       final space = await client.createSpace('/my-vfx-project', 'characters');

       // Create an item (asset)
       final item = await client.createItem(
         '/my-vfx-project/characters',
         'hero',
         'model',
       );

       // Create a revision with artifacts
       final revision = await client.createRevision(item.kref);
       
       // Add a file artifact
       await client.createArtifact(
         revision.kref,
         'hero_model.fbx',
         'file:///projects/hero/hero_model.fbx',
       );
     } finally {
       await client.shutdownAsync();
     }
   }

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   getting-started
   concepts
   authentication
   usage_guide
   configuration

.. toctree::
  :maxdepth: 1
  :caption: API Reference

  api

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
