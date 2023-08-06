import unittest
import numpy as np
from PIL import Image
import time
import lera 

class TestHyperparams(unittest.TestCase):
    def test_it_logs(self):
        to_send = lera.log_hyperparams(u'hello', u'world')
        to_send1 = lera.log_hyperparams(u'hello', u'world')
        to_send3 = lera.log_hyperparams({u'hello1': u'world1'})

        self.assertEqual(to_send['hello'], 'world')
        self.assertEqual(to_send3['hello1'], 'world1')
        with self.assertRaises(KeyError):
            to_send1['hello']

    def test_new_session(self):
        old_session = lera.session
        lera.log_hyperparams('hello', u'world')
        to_send = lera.new_session({'hello' : u'world'})
        self.assertEqual(to_send['hello'], u'world')
        self.assertNotEqual(old_session, lera.session)

    def test_accepted_types(self):
        to_send = lera.new_session({
            'b' : True,
            'i' : 0,
            'f' : 1.0,
            's' : u'hello',
            'unknown' : b'bytes'
            })

        self.assertIn('b', to_send)
        self.assertIn('i', to_send)
        self.assertIn('f', to_send)
        self.assertIn('s', to_send)
        self.assertNotIn('unknown', to_send)

class TestParams(unittest.TestCase):
    def test_it_logs(self):
        to_send = lera.log({
            'b' : True,
            'i' : 0,
            'f' : 1.0,
            's' : 'hello',
            'unknown' : b'hello',
            'dist' : np.random.rand(100),
            })
        self.assertNotIn('b', to_send)
        self.assertIn('i', to_send)
        self.assertIn('f', to_send)
        self.assertNotIn('s', to_send)
        self.assertNotIn('unknown', to_send)
        self.assertIn('dist', to_send)
        self.assertIsInstance(to_send['dist'], list)
        self.assertEqual(len(to_send['dist']), 2)

class TestData(unittest.TestCase):
    def test_types(self):
        s1 = lera.log_data({
            'b' : True,
            'i' : 0,
            'f' : 1.0,
            's' : u'hello',
            'bytes' : b'hello',
            'bytearray' : bytearray(b'hello'),
            })
        self.assertNotIn('file:b', s1)
        self.assertNotIn('file:i', s1)
        self.assertNotIn('file:f', s1)
        self.assertNotIn('file:s', s1)
        self.assertIn('file:bytes', s1)
        self.assertIn('file:bytearray', s1)

    def test_it_logs(self):
        s1 = lera.log_data('test.bin', b'hello')
        self.assertIn('file:test.bin', s1)
        self.assertEqual(s1['file:test.bin'], b'hello')

#TODO test sample_rate, clip
class TestAudio(unittest.TestCase):
    def test_it_logs(self):
        s = lera.log_audio('sample', np.random.randn(1000))
        self.assertIn('audio:sample', s)
        self.assertIsInstance(s['audio:sample'], bytes)
        self.assertTrue(len(s['audio:sample']) > 0)

    def test_types(self):
        s = lera.log_audio({
            'b' : True,
            'i' : 0,
            'f' : 1.0,
            's' : 'hello',
            'bytes' : b'hello',
            'tensor': np.random.randn(1000),
            'tensor1': np.random.randn(1, 1000),
            'tensor2': np.random.randn(3, 1000)
            })
        self.assertNotIn('audio:b', s)
        self.assertNotIn('audio:i', s)
        self.assertNotIn('audio:f', s)
        self.assertNotIn('audio:s', s)
        self.assertNotIn('audio:bytes', s)
        self.assertIn('audio:tensor', s)
        self.assertIn('audio:tensor1', s)
        self.assertNotIn('audio:tensor2', s)


class TestImage(unittest.TestCase):
    def test_it_logs(self):
        tensor = np.random.randn(100, 100, 3)
        s = lera.log_image('img', tensor)
        self.assertIn('image:img', s)
        with self.assertRaises(AssertionError):
            s = lera.log_image('img', np.random.randn(3, 100, 100))
        img = Image.fromarray(tensor.astype('uint8'), 'RGB')
        s = lera.log_image('img', img)
        self.assertIn('image:img', s)

    def test_types(self):
        s = lera.log_image({
            'b' : True,
            'i' : 0,
            'f' : 1.0,
            's' : 'hello'
            })
        self.assertNotIn('image:b', s)
        self.assertNotIn('image:i', s)
        self.assertNotIn('image:f', s)
        self.assertNotIn('image:s', s)


class TestEvery(unittest.TestCase):
    def test_it_logs(self):
        steps = 0
        seconds = 0
        for i in range(10):
            if lera.every(steps=2):
                steps += 1

            if lera.every(seconds=0.33):
                seconds += 1

            time.sleep(0.1)
        self.assertEqual(steps, 5)
        self.assertEqual(seconds, 3)

    def test_required_param(self):
        with self.assertRaises(AssertionError):
            if lera.every():
                print("error!")

if __name__ == '__main__':
    lera.test(True)
    unittest.main()
