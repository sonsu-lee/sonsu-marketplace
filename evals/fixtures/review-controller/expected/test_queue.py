import unittest

from message_queue import flush


class QueueTest(unittest.TestCase):
    def test_success(self):
        queued = ['hello']
        delivered = []
        flush(queued, delivered.append)
        self.assertEqual(delivered, ['hello'])
        self.assertEqual(queued, [])


if __name__ == '__main__':
    unittest.main()
