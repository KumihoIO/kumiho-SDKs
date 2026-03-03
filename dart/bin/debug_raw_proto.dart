// Debug script to examine raw protobuf bytes from server
import 'dart:io';
import 'dart:typed_data';
import 'package:grpc/grpc.dart';
import 'package:kumiho/src/generated/kumiho.pb.dart';
import 'package:kumiho/src/generated/kumiho.pbgrpc.dart';

void main() async {
  final port = int.parse(Platform.environment['KUMIHO_PORT'] ?? '8080');
  String? token;
  
  // Load token
  final home = Platform.environment['USERPROFILE'] ?? Platform.environment['HOME'];
  final tokenFile = File('$home/.kumiho/kumiho_authentication.json');
  if (tokenFile.existsSync()) {
    final content = tokenFile.readAsStringSync();
    final match = RegExp(r'"id_token"\s*:\s*"([^"]+)"').firstMatch(content);
    token = match?.group(1);
  }
  
  if (token == null) {
    print('Could not find token');
    exit(1);
  }
  
  // Create a raw gRPC channel
  final channel = ClientChannel(
    'localhost',
    port: port,
    options: const ChannelOptions(
      credentials: ChannelCredentials.insecure(),
    ),
  );
  
  // Create stub with metadata
  final callOptions = CallOptions(
    metadata: {'authorization': 'Bearer $token'},
  );
  
  final stub = KumihoServiceClient(channel);  // Changed: no options in constructor
  
  // Test with a known kref - you'll need to update this
  // First let's create a project/revision and get its kref
  print('Creating test project...');
  
  final projectName = 'debug_raw_${DateTime.now().millisecondsSinceEpoch}';
  final createProjectReq = CreateProjectRequest()..name = projectName;
  final project = await stub.createProject(createProjectReq, options: callOptions);
  print('Created project: ${project.name}');
  
  try {
    // Create space
    final createSpaceReq = CreateSpaceRequest()
      ..spaceName = projectName
      ..parentPath = '/${project.name}';
    final space = await stub.createSpace(createSpaceReq, options: callOptions);
    print('Created space: ${space.path}');
    
    // Create item
    final createItemReq = CreateItemRequest()
      ..parentPath = space.path
      ..itemName = 'asset'
      ..kind = 'model';
    final item = await stub.createItem(createItemReq, options: callOptions);
    print('Created item: ${item.kref.uri}');
    
    // Create revision
    final createRevReq = CreateRevisionRequest()..itemKref = item.kref;
    final revision = await stub.createRevision(createRevReq, options: callOptions);
    print('Created revision: ${revision.kref.uri}');
    
    // Create artifact
    final createArtReq = CreateArtifactRequest()
      ..revisionKref = revision.kref
      ..name = 'main'
      ..location = '/path/to/file';
    final artifact = await stub.createArtifact(createArtReq, options: callOptions);
    print('Created artifact: ${artifact.kref.uri}');
    
    // Set default artifact
    print('\nSetting default artifact...');
    final setDefaultReq = SetDefaultArtifactRequest()
      ..revisionKref = revision.kref
      ..artifactName = 'main';
    await stub.setDefaultArtifact(setDefaultReq, options: callOptions);
    print('Set default artifact to "main"');
    
    // Now get the revision and examine the response
    print('\n=== Getting revision ===');
    final getRevReq = KrefRequest()..kref = revision.kref;
    final revResponse = await stub.getRevision(getRevReq, options: callOptions);
    
    print('Response fields:');
    print('  kref: ${revResponse.kref.uri}');
    print('  number: ${revResponse.number}');
    print('  name: "${revResponse.name}"');
    print('  username: "${revResponse.username}"');
    print('  defaultArtifact: "${revResponse.defaultArtifact}"');
    print('  hasDefaultArtifact(): ${revResponse.hasDefaultArtifact()}');
    
    // Serialize the response to bytes and print
    final bytes = revResponse.writeToBuffer();
    print('\n=== Serialized response ===');
    print('Length: ${bytes.length} bytes');
    
    // Look for the defaultArtifact field (tag 13, wire type 2 = length-delimited)
    // Tag 13 wire type 2 = (13 << 3) | 2 = 106 = 0x6A
    print('\nSearching for tag 13 (0x6A) in bytes...');
    for (var i = 0; i < bytes.length; i++) {
      if (bytes[i] == 0x6A) {
        print('  Found 0x6A at position $i');
        if (i + 1 < bytes.length) {
          final len = bytes[i + 1];
          print('    Length: $len');
          if (i + 2 + len <= bytes.length) {
            final value = String.fromCharCodes(bytes.sublist(i + 2, i + 2 + len));
            print('    Value: "$value"');
          }
        }
      }
    }
    
    // Print raw bytes in hex
    print('\nRaw bytes (hex):');
    final hexStr = bytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join(' ');
    print(hexStr);
    
  } finally {
    // Cleanup
    print('\n=== Cleanup ===');
    try {
      final deleteReq = DeleteProjectRequest()..projectId = projectName;
      await stub.deleteProject(deleteReq, options: callOptions);
      print('Deleted project');
    } catch (e) {
      print('Failed to delete: $e');
    }
    await channel.shutdown();
  }
}
