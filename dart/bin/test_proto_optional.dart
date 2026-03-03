// Test protobuf encoding/decoding of optional string fields
import 'dart:typed_data';
import 'package:kumiho/src/generated/kumiho.pb.dart';

void main() {
  // Create a RevisionResponse with defaultArtifact set
  final response = RevisionResponse()
    ..kref = (Kref()..uri = 'kref://test/test/item.model?r=1')
    ..itemKref = (Kref()..uri = 'kref://test/test/item.model')
    ..number = 1
    ..name = 'v1'
    ..username = 'testuser'
    ..defaultArtifact = 'main';

  print('=== Original response ===');
  print('defaultArtifact: "${response.defaultArtifact}"');
  print('hasDefaultArtifact(): ${response.hasDefaultArtifact()}');
  print('name: "${response.name}"');
  print('hasName(): ${response.hasName()}');

  // Serialize to bytes
  final bytes = response.writeToBuffer();
  print('\n=== Serialized bytes ===');
  print('Length: ${bytes.length}');
  print('Hex: ${bytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join(' ')}');

  // Deserialize back
  final deserialized = RevisionResponse.fromBuffer(bytes);
  print('\n=== Deserialized response ===');
  print('defaultArtifact: "${deserialized.defaultArtifact}"');
  print('hasDefaultArtifact(): ${deserialized.hasDefaultArtifact()}');
  print('name: "${deserialized.name}"');
  print('hasName(): ${deserialized.hasName()}');

  // Test without setting defaultArtifact
  print('\n=== Response without defaultArtifact ===');
  final response2 = RevisionResponse()
    ..kref = (Kref()..uri = 'kref://test/test/item.model?r=1')
    ..itemKref = (Kref()..uri = 'kref://test/test/item.model')
    ..number = 1
    ..name = 'v1'
    ..username = 'testuser';
  
  print('defaultArtifact: "${response2.defaultArtifact}"');
  print('hasDefaultArtifact(): ${response2.hasDefaultArtifact()}');
  
  final bytes2 = response2.writeToBuffer();
  print('\nSerialized length: ${bytes2.length}');
  
  final deserialized2 = RevisionResponse.fromBuffer(bytes2);
  print('\nAfter deserialize:');
  print('defaultArtifact: "${deserialized2.defaultArtifact}"');
  print('hasDefaultArtifact(): ${deserialized2.hasDefaultArtifact()}');
}
