// Opt-in real CE probe. The endpoint/root belong to a disposable local fixture.
import 'dart:convert';
import 'package:kumiho/kumiho.dart';
import 'package:kumiho/src/models/space.dart' as models;

void require(bool ok) {
  if (!ok) throw StateError('inventory compatibility assertion failed');
}

Future<void> main(List<String> args) async {
  final split = args[0].split(':');
  final client = KumihoClient(
    host: split[0],
    port: int.parse(split[1]),
    autoLoadToken: false,
  );
  try {
    final root = args[1];
    final legacy = await client.getChildSpaces(root, recursive: true);
    require(legacy.length == 1004 && legacy is PagedList<SpaceResponse>);
    final space = models.Space(SpaceResponse(path: root), client);
    final all = await space.getItems(includeDeprecated: true);
    require(
      all.length == 1004 &&
          all.totalCount == 1004 &&
          all.paginationPresent &&
          all.hasMore == false,
    );
    for (final kind in ['spaces', 'items']) {
      String? cursor;
      final ids = <String>{};
      var count = 0;
      while (true) {
        if (kind == 'spaces') {
          final page = await space.getChildSpacesPaged(
            recursive: true,
            pageSize: 251,
            cursor: cursor,
          );
          require(
            page.paginationPresent &&
                page.totalCount == 1004 &&
                page.length == 251,
          );
          ids.addAll(page.map((s) => s.path));
          count += page.length;
          cursor = page.nextCursor;
          require(page.hasMore == (cursor != null && cursor.isNotEmpty));
        } else {
          final page = await space.getItems(
            includeDeprecated: true,
            pageSize: 251,
            cursor: cursor,
          );
          require(
            page.paginationPresent &&
                page.totalCount == 1004 &&
                page.length == 251,
          );
          ids.addAll(page.map((i) => i.kref.uri));
          count += page.length;
          cursor = page.nextCursor;
          require(page.hasMore == (cursor != null && cursor.isNotEmpty));
        }
        if (cursor == null || cursor.isEmpty) break;
      }
      require(count == 1004 && ids.length == 1004);
    }
    print(
      jsonEncode({
        'sdk': 'Dart fixed',
        'unpaged': 1004,
        'pages': [251, 251, 251, 251],
        'metadata_present': true,
        'result': 'PASS',
      }),
    );
  } finally {
    await client.channel.shutdown();
  }
}
