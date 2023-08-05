from bomojo.tests import TestCase



class MovieTestCase(TestCase):
    def setUp(self):
        self.movie = self.create_movie(title='Unbreakable',
                                       external_id='unbreakable')

    def test_str(self):
        self.assertEqual('Unbreakable (unbreakable)', str(self.movie))

    def test_repr(self):
        self.assertEqual('<Movie: Unbreakable (unbreakable)>', repr(self.movie))
