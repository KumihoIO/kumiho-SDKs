import 'dart:io';
import 'package:grpc/grpc.dart';
import 'package:kumiho/kumiho.dart';
import 'package:kumiho/src/generated/kumiho.pb.dart' as pb;
import 'package:kumiho/src/models/item.dart' as models;
import 'package:kumiho/src/models/revision.dart' as models;
import 'package:test/test.dart';

/// Serves scripted GetRevisions/GetEdges responses in order and records every
/// request.
class _PagingService extends KumihoServiceBase {
  final revisionPages = <GetRevisionsResponse>[];
  final edgePages = <GetEdgesResponse>[];
  final revisionRequests = <GetRevisionsRequest>[];
  final edgeRequests = <GetEdgesRequest>[];

  @override
  Future<GetRevisionsResponse> getRevisions(
    ServiceCall call,
    GetRevisionsRequest request,
  ) async {
    revisionRequests.add(request);
    if (revisionPages.isEmpty) throw GrpcError.unimplemented('GetRevisions');
    return revisionPages.removeAt(0);
  }

  @override
  Future<GetEdgesResponse> getEdges(
    ServiceCall call,
    GetEdgesRequest request,
  ) async {
    edgeRequests.add(request);
    if (edgePages.isEmpty) throw GrpcError.unimplemented('GetEdges');
    return edgePages.removeAt(0);
  }

  @override
  dynamic noSuchMethod(Invocation invocation) =>
      throw GrpcError.unimplemented();
}

PaginationResponse _more(String cursor) =>
    PaginationResponse(nextCursor: cursor, hasMore: true, totalCount: -1);

PaginationResponse _done() => PaginationResponse(totalCount: -1);

GetRevisionsResponse _revs(List<int> numbers, PaginationResponse? page) {
  final response = GetRevisionsResponse(
    revisions: [
      for (final n in numbers)
        RevisionResponse(
          kref: pb.Kref(uri: 'kref://p/s/x.k?r=$n'),
          itemKref: pb.Kref(uri: 'kref://p/s/x.k'),
          number: n,
        ),
    ],
  );
  if (page != null) response.pagination = page;
  return response;
}

GetEdgesResponse _edges(List<int> targets, PaginationResponse? page) {
  final response = GetEdgesResponse(
    edges: [
      for (final n in targets)
        pb.Edge(
          sourceKref: pb.Kref(uri: 'kref://p/s/x.k?r=1'),
          targetKref: pb.Kref(uri: 'kref://p/s/y.k?r=$n'),
          edgeType: 'DEPENDS_ON',
        ),
    ],
  );
  if (page != null) response.pagination = page;
  return response;
}

void main() {
  late Server server;
  late _PagingService service;
  late KumihoClient client;

  setUp(() async {
    service = _PagingService();
    server = Server.create(services: [service]);
    await server.serve(address: InternetAddress.loopbackIPv4, port: 0);
    client = KumihoClient(
      host: '127.0.0.1',
      port: server.port!,
      autoLoadToken: false,
    );
  });
  tearDown(() async {
    await client.channel.shutdown();
    await server.shutdown();
  });

  Future<List<int>> revisionNumbers() async =>
      (await client.getRevisions(
        'kref://p/s/x.k',
      )).map((r) => r.number).toList();

  Future<List<String>> edgeTargets() async =>
      (await client.getEdges(
        'kref://p/s/x.k?r=1',
        direction: pb.EdgeDirection.BOTH,
      )).edges.map((e) => e.targetKref.uri).toList();

  List<(int, String)> sent(Iterable<dynamic> requests) => [
    for (final r in requests)
      (r.pagination.pageSize as int, r.pagination.cursor as String),
  ];

  test(
    'getRevisions follows every page, including an empty middle page',
    () async {
      service.revisionPages.addAll([
        _revs([5, 4], _more('c1')),
        _revs([], _more('c2')),
        _revs([3, 2, 1], _done()),
      ]);
      expect(await revisionNumbers(), [5, 4, 3, 2, 1]);
      expect(sent(service.revisionRequests), [
        (1000, ''),
        (1000, 'c1'),
        (1000, 'c2'),
      ]);
    },
  );

  test('getEdges follows every page, including an empty middle page', () async {
    service.edgePages.addAll([
      _edges([1, 2], _more('c1')),
      _edges([], _more('c2')),
      _edges([3], _done()),
    ]);
    expect(await edgeTargets(), [
      'kref://p/s/y.k?r=1',
      'kref://p/s/y.k?r=2',
      'kref://p/s/y.k?r=3',
    ]);
    expect(sent(service.edgeRequests), [
      (1000, ''),
      (1000, 'c1'),
      (1000, 'c2'),
    ]);
  });

  test('models reach every page too', () async {
    service.revisionPages.addAll([
      _revs([2], _more('c1')),
      _revs([1], _done()),
    ]);
    service.edgePages.addAll([
      _edges([1], _more('c1')),
      _edges([2], _done()),
    ]);
    final item = models.Item(
      ItemResponse(kref: pb.Kref(uri: 'kref://p/s/x.k')),
      client,
    );
    expect((await item.getRevisions()).length, 2);
    final revision = models.Revision(
      RevisionResponse(
        kref: pb.Kref(uri: 'kref://p/s/x.k?r=1'),
        itemKref: pb.Kref(uri: 'kref://p/s/x.k'),
      ),
      client,
    );
    expect((await revision.getEdges()).length, 2);
  });

  test('a missing pagination field is one complete response', () async {
    // kumiho-server CE answers GetEdges with every edge and no pagination.
    service.edgePages.add(_edges([1, 2, 3], null));
    service.revisionPages.add(_revs([2, 1], null));
    expect((await edgeTargets()).length, 3);
    expect(await revisionNumbers(), [2, 1]);
    expect(service.edgeRequests.length, 1);
    expect(service.revisionRequests.length, 1);
  });

  test('a repeated cursor is an error, not a loop', () async {
    service.edgePages.addAll([
      _edges([1], _more('c1')),
      _edges([2], _more('c1')),
    ]);
    service.revisionPages.addAll([
      _revs([3], _more('a')),
      _revs([2], _more('b')),
      _revs([1], _more('a')),
    ]);
    final advance = isA<KumihoError>().having(
      (e) => e.message,
      'message',
      contains('did not advance'),
    );
    await expectLater(edgeTargets(), throwsA(advance));
    await expectLater(revisionNumbers(), throwsA(advance));
  });

  test('hasMore without a cursor is an error', () async {
    service.edgePages.add(_edges([1], _more('')));
    service.revisionPages.add(_revs([1], _more('')));
    final noCursor = isA<KumihoError>().having(
      (e) => e.message,
      'message',
      contains('no pagination cursor'),
    );
    await expectLater(edgeTargets(), throwsA(noCursor));
    await expectLater(revisionNumbers(), throwsA(noCursor));
  });

  test('the CE offset shift does not repeat a revision', () async {
    // CE pages GetRevisions by offset, newest first. Revision 4 is created
    // after the first page, so the second page starts one row later and
    // repeats revision 2.
    service.revisionPages.addAll([
      _revs([3, 2], _more('offset:2')),
      _revs([2, 1], _done()),
    ]);
    expect(await revisionNumbers(), [3, 2, 1]);
  });

  test('single-page APIs return one page with its cursor', () async {
    service.revisionPages.add(_revs([2], _more('r-next')));
    service.edgePages.add(_edges([1], _more('e-next')));
    final revisions = await client.getRevisionsPaged(
      'kref://p/s/x.k',
      pageSize: 1,
      cursor: 'r-prev',
    );
    expect(revisions.length, 1);
    expect(revisions.nextCursor, 'r-next');
    expect(revisions.hasMore, isTrue);
    expect(revisions.paginationPresent, isTrue);
    final edges = await client.getEdgesPaged('kref://p/s/x.k?r=1', pageSize: 5);
    expect(edges.nextCursor, 'e-next');
    expect(sent(service.revisionRequests), [(1, 'r-prev')]);
    expect(sent(service.edgeRequests), [(5, '')]);
  });
}
