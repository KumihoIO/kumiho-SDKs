API Reference
=============

The API reference is generated automatically from Dart documentation comments
(Dartdoc) during the documentation build.

- Open the generated API docs: `dartdoc/index.html <dartdoc/index.html>`_

The public surface is the ``KumihoClient`` class (in ``package:kumiho/kumiho.dart``)
and the fluent model types in ``package:kumiho/models.dart``. ``KumihoClient``
composes the per-resource API mixins (project, space, item, revision, artifact,
edge, bundle, event, tenant, attribute), including ``search``, ``scoreRevisions``,
``batchGetRevisions``, the by-kref accessors (``getItemFromRevision``,
``getArtifactByKref``, ``getBundleByKref``), and event streaming
(``eventStream``, ``getEventCapabilities``).
