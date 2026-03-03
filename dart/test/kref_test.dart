// SPDX-License-Identifier: MIT
// Copyright (c) 2025 kumihoclouds

import 'package:test/test.dart';
import 'package:kumiho/kumiho.dart';

void main() {
  group('Kref', () {
    group('parsing', () {
      test('parses item kref correctly', () {
        final kref = Kref('kref://my-project/models/hero.model');

        expect(kref.project, equals('my-project'));
        expect(kref.space, equals('models'));
        expect(kref.itemName, equals('hero'));
        expect(kref.kind, equals('model'));
        expect(kref.fullItemName, equals('hero.model'));
        expect(kref.revision, isNull);
        expect(kref.artifactName, isNull);
      });

      test('parses revision kref correctly', () {
        final kref = Kref('kref://my-project/models/hero.model?r=3');

        expect(kref.project, equals('my-project'));
        expect(kref.space, equals('models'));
        expect(kref.itemName, equals('hero'));
        expect(kref.kind, equals('model'));
        expect(kref.revision, equals(3));
        expect(kref.artifactName, isNull);
      });

      test('parses artifact kref correctly', () {
        final kref = Kref('kref://my-project/models/hero.model?r=2&a=mesh');

        expect(kref.project, equals('my-project'));
        expect(kref.space, equals('models'));
        expect(kref.itemName, equals('hero'));
        expect(kref.kind, equals('model'));
        expect(kref.revision, equals(2));
        expect(kref.artifactName, equals('mesh'));
      });

      test('parses nested space path correctly', () {
        final kref = Kref('kref://project/chars/heroes/main/hero.model');

        expect(kref.project, equals('project'));
        expect(kref.space, equals('chars/heroes/main'));
        expect(kref.itemName, equals('hero'));
        expect(kref.kind, equals('model'));
      });

      test('handles project-level items', () {
        final kref = Kref('kref://project/space/item.texture');

        expect(kref.project, equals('project'));
        expect(kref.space, equals('space'));
        expect(kref.itemName, equals('item'));
        expect(kref.kind, equals('texture'));
      });
    });

    group('validation', () {
      test('accepts valid krefs', () {
        expect(() => Kref('kref://project/space/item.kind'), returnsNormally);
        expect(() => Kref('kref://project/item.kind'), returnsNormally);
        expect(() => Kref('kref://project/space/item.kind?r=1'), returnsNormally);
        expect(
            () => Kref('kref://project/space/item.kind?r=1&a=mesh'), returnsNormally);
      });

      test('rejects path traversal attempts', () {
        expect(
          () => Kref('kref://project/../secret/item.kind'),
          throwsA(isA<KrefValidationError>()),
        );
      });

      test('rejects control characters', () {
        expect(
          () => Kref('kref://project/space/item\x00.kind'),
          throwsA(isA<KrefValidationError>()),
        );
      });

      test('rejects invalid format', () {
        expect(
          () => Kref('invalid://project/item.kind'),
          throwsA(isA<KrefValidationError>()),
        );
        expect(
          () => Kref('kref://'),
          throwsA(isA<KrefValidationError>()),
        );
      });
    });

    group('helper methods', () {
      test('withRevision creates revision kref', () {
        final itemKref = Kref('kref://project/space/item.model');
        final revKref = itemKref.withRevision(5);

        expect(revKref.uri, equals('kref://project/space/item.model?r=5'));
        expect(revKref.revision, equals(5));
      });

      test('withArtifact creates artifact kref', () {
        final revKref = Kref('kref://project/space/item.model?r=3');
        final artKref = revKref.withArtifact('textures');

        expect(
            artKref.uri, equals('kref://project/space/item.model?r=3&a=textures'));
        expect(artKref.artifactName, equals('textures'));
      });

      test('withArtifact throws if no revision', () {
        final itemKref = Kref('kref://project/space/item.model');

        expect(
          () => itemKref.withArtifact('mesh'),
          throwsA(isA<StateError>()),
        );
      });

      test('itemKref extracts item reference', () {
        final artKref = Kref('kref://project/space/item.model?r=2&a=mesh');
        final itemKref = artKref.itemKref;

        expect(itemKref.uri, equals('kref://project/space/item.model'));
        expect(itemKref.revision, isNull);
        expect(itemKref.artifactName, isNull);
      });

      test('revisionKref extracts revision reference', () {
        final artKref = Kref('kref://project/space/item.model?r=2&a=mesh');
        final revKref = artKref.revisionKref;

        expect(revKref?.uri, equals('kref://project/space/item.model?r=2'));
        expect(revKref?.artifactName, isNull);
      });
    });

    group('equality', () {
      test('equal krefs are equal', () {
        final kref1 = Kref('kref://project/space/item.model?r=1');
        final kref2 = Kref('kref://project/space/item.model?r=1');

        expect(kref1, equals(kref2));
        expect(kref1.hashCode, equals(kref2.hashCode));
      });

      test('different krefs are not equal', () {
        final kref1 = Kref('kref://project/space/item.model?r=1');
        final kref2 = Kref('kref://project/space/item.model?r=2');

        expect(kref1, isNot(equals(kref2)));
      });
    });

    group('isValidKref', () {
      test('returns true for valid krefs', () {
        expect(isValidKref('kref://project/space/item.kind'), isTrue);
        expect(isValidKref('kref://project/item.kind?r=1&a=mesh'), isTrue);
      });

      test('returns false for invalid krefs', () {
        expect(isValidKref('invalid://project/item.kind'), isFalse);
        expect(isValidKref('kref://project/../item.kind'), isFalse);
        expect(isValidKref(''), isFalse);
      });
    });
  });
}
