.. Kumiho Python SDK documentation master file

Kumiho Python SDK
=================

**Graph-native creative & AI asset management for Python**

.. image:: https://img.shields.io/pypi/v/kumiho.svg
   :target: https://pypi.org/project/kumiho/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/kumiho.svg
   :target: https://pypi.org/project/kumiho/
   :alt: Python versions

.. image:: https://readthedocs.org/projects/kumiho/badge/?version=latest
   :target: https://kumiho.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

Kumiho is a Python SDK for `Kumiho Cloud <https://kumiho.io>`_, a graph-native
creative and AI asset management platform designed for VFX, animation, and
AI-driven workflows.

Key Features
------------

- **Graph-Native Design**: Built on Neo4j for tracking asset relationships and lineage
- **Version Control**: Semantic versioning for creative assets with full history
- **AI Lineage Tracking**: Track AI model training data provenance and dependencies
- **BYO Storage**: Files stay on your local/NAS/on-prem storage
- **Multi-Tenant SaaS**: Secure, region-aware multi-tenant architecture

Quick Start
-----------

Installation
^^^^^^^^^^^^

.. code-block:: bash

   pip install kumiho

Authentication
^^^^^^^^^^^^^^

First, authenticate with Kumiho Cloud:

.. code-block:: bash

   kumiho-auth

This will open a browser for Firebase authentication and cache your credentials.

Basic Usage
^^^^^^^^^^^

.. code-block:: python

   import kumiho

   # Connect to Kumiho Cloud (uses cached credentials)
   kumiho.connect()

   # Create a new project
   project = kumiho.create_project(
       name="my-vfx-project",
       description="My VFX Project for 2024 film"
   )

   # Create an asset space
   space = project.create_space("characters")

   # Create an item (asset)
   item = space.create_item(
       item_name="hero",
       kind="model"
   )

   # Create a revision with artifacts
   revision = item.create_revision(
       description="Initial model with rigging"
   )
   
   # Add a file artifact
   artifact = revision.create_artifact(
       name="hero_model.fbx",
       location="file:///projects/hero/hero_model.fbx"
   )

   # Reference assets using Kref URIs
   kref = "kref://my-vfx-project/characters/hero.model?v=1&r=hero_model.fbx"
   artifact = kumiho.get_artifact(kref)

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   getting-started
   concepts
   authentication

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/kumiho
   api/project
   api/space
   api/item
   api/bundle
   api/revision
   api/artifact
   api/edge
   api/kref

.. toctree::
   :maxdepth: 1
   :caption: Development

   changelog
   contributing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
