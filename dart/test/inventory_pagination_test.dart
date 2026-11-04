import 'dart:io';
import 'package:grpc/grpc.dart';
import 'package:kumiho/kumiho.dart';
import 'package:kumiho/src/generated/kumiho.pb.dart' as pb;
import 'package:kumiho/src/models/space.dart' as models;
import 'package:kumiho/src/models/project.dart' as models;
import 'package:kumiho/src/models/item.dart' as models;
import 'package:test/test.dart';

class _InventoryService extends KumihoServiceBase {
  bool withMetadata = true;
  GetChildSpacesRequest? spacesRequest;
  GetItemsRequest? itemsRequest;

  @override
  Future<GetChildSpacesResponse> getChildSpaces(
    ServiceCall call,
    GetChildSpacesRequest request,
  ) async {
    spacesRequest = request;
    final response = GetChildSpacesResponse();
    if (withMetadata) {
      response.pagination = PaginationResponse(
        totalCount: 8,
        hasMore: true,
        nextCursor: 'opaque-next',
      );
    }
    return response;
  }

  @override
  Future<GetItemsResponse> getItems(
    ServiceCall call,
    GetItemsRequest request,
  ) async {
    itemsRequest = request;
    final response = GetItemsResponse();
    if (withMetadata)
      response.pagination = PaginationResponse(
        totalCount: 0,
        hasMore: false,
        nextCursor: '',
      );
    return response;
  }

  @override
  dynamic noSuchMethod(Invocation invocation) =>
      throw GrpcError.unimplemented();
}

void main() {
  test(
    'server inventory retains safe dot-prefixed identities without relaxing requests',
    () {
      const uri = 'kref://p/.assets/.hidden.fact';
      expect(() => Kref(uri), throwsA(isA<KrefValidationError>()));
      final item = models.Item(ItemResponse(kref: pb.Kref(uri: uri)), null);
      expect(item.kref.uri, uri);
      for (final invalid in [
        'kref://p/../secret.note',
        'kref://p/.bad\u0000.note',
        'kref://p/.hidden.',
      ]) {
        expect(
          () => models.Item(ItemResponse(kref: pb.Kref(uri: invalid)), null),
          throwsA(isA<KrefValidationError>()),
        );
      }
    },
  );
  late Server server;
  late _InventoryService service;
  late KumihoClient client;
  setUp(() async {
    service = _InventoryService();
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

  test(
    'model space/project mapping preserves page metadata and opaque cursor',
    () async {
      final space = models.Space(SpaceResponse(path: '/p'), client);
      final legacy = await space.getChildSpaces();
      expect(legacy, isA<List<models.Space>>());
      expect(service.spacesRequest!.hasPagination(), isFalse);
      expect(legacy, isA<PagedList<models.Space>>());
      final page = await space.getChildSpacesPaged(
        recursive: true,
        pageSize: 2,
        cursor: 'opaque-before',
      );
      expect(page.paginationPresent, isTrue);
      expect(page.hasMore, isTrue);
      expect(page.totalCount, 8);
      expect(page.nextCursor, 'opaque-next');
      expect(service.spacesRequest!.recursive, isTrue);
      expect(service.spacesRequest!.pagination.cursor, 'opaque-before');
      final project = models.Project(ProjectResponse(name: 'p'), client);
      final projectPage = await project.getSpacesPaged(pageSize: 2);
      expect(projectPage.paginationPresent, isTrue);
      expect(projectPage.totalCount, 8);
    },
  );

  test(
    'empty final page differs from missing metadata and deprecated is forwarded',
    () async {
      final space = models.Space(SpaceResponse(path: '/p'), client);
      final page = await space.getItems(includeDeprecated: true);
      expect(page, isEmpty);
      expect(page.paginationPresent, isTrue);
      expect(page.hasMore, isFalse);
      expect(page.totalCount, 0);
      expect(page.nextCursor, '');
      expect(service.itemsRequest!.includeDeprecated, isTrue);
      expect(service.itemsRequest!.hasPagination(), isFalse);
      service.withMetadata = false;
      final missing = await space.getChildSpacesPaged();
      expect(missing.paginationPresent, isFalse);
      expect(missing.hasMore, isNull);
      expect(missing.totalCount, isNull);
      expect(missing.nextCursor, isNull);
    },
  );
}
