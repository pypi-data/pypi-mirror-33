# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bomojo.tests import TestCase


class MatchupTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.bob = cls.create_user('bob')
        cls.alice = cls.create_user('alice')

    def test_matchup_populates_slug_on_save(self):
        matchup = self.bob.matchups.create(title='foo vs bar',
                                           movies=['foo', 'bar'])
        self.assertEqual('foo-vs-bar', matchup.slug)

    def test_slug_is_always_unique(self):
        bob_matchup = self.bob.matchups.create(title='foo vs bar',
                                               movies=['foo', 'bar'])
        alice_matchup = self.alice.matchups.create(title='foo vs bar',
                                                   movies=['foo', 'bar'])

        self.assertIn('foo-vs-bar', bob_matchup.slug)
        self.assertIn('foo-vs-bar', alice_matchup.slug)
        self.assertNotEqual(bob_matchup.slug, alice_matchup.slug)

    def test_slug_does_not_change(self):
        matchup = self.bob.matchups.create(title='foo vs bar',
                                           movies=['foo', 'bar'])
        self.assertEqual('foo-vs-bar', matchup.slug)

        matchup.title = 'bar vs foo'
        matchup.save()
        matchup.refresh_from_db()
        self.assertEqual('foo-vs-bar', matchup.slug)
