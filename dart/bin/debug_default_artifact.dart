// Debug script to verify default_artifact is working correctly.
// Run: dart run bin/debug_default_artifact.dart
import 'dart:io';
import 'dart:math';
import 'package:kumiho/kumiho.dart';
import 'package:kumiho/src/generated/kumiho.pb.dart' as pb;

String uniqueName(String prefix) {
  final random = Random();
  final suffix = random.nextInt(99999999).toRadixString(36);
  return '${prefix}_$suffix';
}

Future<void> main() async {
  // Connect using environment token
  final port = int.parse(Platform.environment['KUMIHO_PORT'] ?? '8080');
  String? token = Platform.environment['KUMIHO_TOKEN'];
  
  // Try to load token from cache if not in environment
  if (token == null) {
    final home = Platform.environment['USERPROFILE'] ?? Platform.environment['HOME'];
    final tokenFile = File('$home/.kumiho/kumiho_authentication.json');
    if (tokenFile.existsSync()) {
      final content = tokenFile.readAsStringSync();
      // Simple JSON parse for id_token
      final match = RegExp(r'"id_token"\s*:\s*"([^"]+)"').firstMatch(content);
      token = match?.group(1);
      if (token != null) {
        print('Loaded token from cache');
      }
    }
  }
  
  if (token == null) {
    print('Could not find token - set KUMIHO_TOKEN or run "dart run bin/login.dart"');
    exit(1);
  }
  
  final client = KumihoClient(
    host: 'localhost',
    port: port,
    token: token,
    secure: false,
  );
  
  final projectName = uniqueName('debug_proj');
  print('Creating project: $projectName');
  
  try {
    final project = await client.newProject(projectName);
    final space = await project.createSpace(projectName);
    final item = await space.createItem('asset', 'model');
    final revision = await item.createRevision();
    final artifact = await revision.createArtifact('main', '/path/to/file');
    
    print('\n=== Before setDefaultArtifact ===');
    print('revision.defaultArtifact = "${revision.defaultArtifact}"');
    
    print('\n=== Calling setDefaultArtifact("main") ===');
    await revision.setDefaultArtifact('main');
    print('setDefaultArtifact completed');
    
    print('\n=== After setDefaultArtifact (before reload) ===');
    print('revision.defaultArtifact = "${revision.defaultArtifact}"');
    
    print('\n=== Reloading revision via getRevision (raw pb) ===');
    // Call stub directly instead of going through API - use generated Kref
    final krefPb = pb.Kref()..uri = revision.kref.uri;
    print('Using kref URI: ${revision.kref.uri}');
    print('krefPb.uri: ${krefPb.uri}');
    final getRevReq = pb.KrefRequest()..kref = krefPb;
    print('getRevReq.kref.uri: ${getRevReq.kref.uri}');
    print('Calling stub.getRevision with callOptions...');
    print('callOptions.metadata: ${client.callOptions.metadata}');
    final reloadedPb = await client.stub.getRevision(getRevReq, options: client.callOptions);
    
    print('\n=== After reload (raw pb) ===');
    print('reloadedPb.defaultArtifact = "${reloadedPb.defaultArtifact}"');
    print('reloadedPb.hasDefaultArtifact() = ${reloadedPb.hasDefaultArtifact()}');
    print('reloadedPb.name = "${reloadedPb.name}"');
    print('reloadedPb.username = "${reloadedPb.username}"');
    
    print('\n=== Reloading via client.revision (model) ===');
    final reloadedModel = await client.revision(revision.kref.uri);
    print('reloadedModel.defaultArtifact = "${reloadedModel.defaultArtifact}"');
    
    print('\n=== RESULT ===');
    if (reloadedPb.defaultArtifact == 'main') {
      print('SUCCESS: default_artifact is "main"');
    } else {
      print('FAILURE: default_artifact is "${reloadedPb.defaultArtifact}"');
    }
    
  } finally {
    print('\n=== Cleanup ===');
    try {
      await client.deleteProject(projectName);
      print('Project deleted');
    } catch (e) {
      print('Failed to delete project: $e');
    }
  }
}
