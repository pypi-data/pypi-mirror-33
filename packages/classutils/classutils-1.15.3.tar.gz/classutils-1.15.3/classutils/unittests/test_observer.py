# -*- coding: utf-8 -*-

import unittest
import logging_helper
from time import sleep
from classutils.observer import (Observable,
                                 Observer,
                                 ObserverError)

logging = logging_helper.setup_logging()


class CheckObservable(Observable):
    pass


class CheckObserver(Observer):

    def __init__(self):
        self.dummy = None

    def notification(self,
                     **kwargs):
        if u'dummy' in kwargs:
            self.dummy = kwargs[u'dummy']


class CheckBadObserver(object):

    def notification(self,
                     **kwargs):
        pass


class CheckDeprecatedObserver(Observer):

    def notify(self,
               **kwargs):
        pass


class CheckBadDeprecatedObserver(object):

    def notify(self,
               **kwargs):
        pass


class UnObservable(object):
    pass


class TestObservable(unittest.TestCase):

    def setUp(self):
        self.observable = CheckObservable()

    def tearDown(self):
        for observer in self.observable.observers:
            self.observable.unregister_observer(observer)

    # Test Observer sub-classes
    def test_register_observer(self):
        self.observable.register_observer(CheckObserver())
        self.observable.register_observer(CheckDeprecatedObserver())

    def test_unregister_observer(self):
        obs = CheckObserver()
        obs_depr = CheckDeprecatedObserver()
        self.observable.register_observer(obs)
        self.observable.register_observer(obs_depr)

        self.assertIn(obs, self.observable.observers, u'')
        self.assertIn(obs_depr, self.observable.observers, u'')

        self.observable.unregister_observer(obs)
        self.observable.unregister_observer(obs_depr)

    def test_observed(self):
        obs = CheckObserver()
        obs_depr = CheckDeprecatedObserver()
        self.assertFalse(self.observable.observed)
        self.observable.register_observer(obs)
        self.assertTrue(self.observable.observed)
        self.observable.register_observer(obs_depr)
        self.assertTrue(self.observable.observed)
        self.observable.unregister_observer(obs)
        self.assertTrue(self.observable.observed)
        self.observable.unregister_observer(obs_depr)
        self.assertFalse(self.observable.observed)

    def test_observer_count(self):
        obs = CheckObserver()
        obs_depr = CheckDeprecatedObserver()
        self.assertEquals(self.observable.observer_count, 0)
        self.observable.register_observer(obs)
        self.assertEquals(self.observable.observer_count, 1)
        self.observable.register_observer(obs_depr)
        self.assertEquals(self.observable.observer_count, 2)
        self.observable.unregister_observer(obs)
        self.assertEquals(self.observable.observer_count, 1)
        self.observable.unregister_observer(obs_depr)
        self.assertEquals(self.observable.observer_count, 0)

    def test_observed_by(self):
        obs = CheckObserver()
        obs_depr = CheckDeprecatedObserver()
        self.assertFalse(self.observable.observed_by(obs))
        self.assertFalse(self.observable.observed_by(obs_depr))
        self.observable.register_observer(obs)
        self.assertTrue(self.observable.observed_by(obs))
        self.assertFalse(self.observable.observed_by(obs_depr))
        self.observable.register_observer(obs_depr)
        self.assertTrue(self.observable.observed_by(obs))
        self.assertTrue(self.observable.observed_by(obs_depr))
        self.observable.unregister_observer(obs)
        self.assertFalse(self.observable.observed_by(obs))
        self.assertTrue(self.observable.observed_by(obs_depr))
        self.observable.unregister_observer(obs_depr)
        self.assertFalse(self.observable.observed_by(obs))
        self.assertFalse(self.observable.observed_by(obs_depr))

    # Test bad observers
    def test_bad_register_observer(self):
        with self.assertRaises(ObserverError):
            self.observable.register_observer(CheckBadObserver())

        with self.assertRaises(ObserverError):
            self.observable.register_observer(CheckBadDeprecatedObserver())

    # Test registration observer missing required methods
    def test_register_non_observable(self):
        with self.assertRaises(ObserverError):
            self.observable.register_observer(UnObservable())

    # Test notifications
    def test_notify_observers(self):
        message = u'dummy_message'
        obs = CheckObserver()

        self.observable.register_observer(obs)
        self.observable.notify_observers(dummy=message)

        sleep(0.5)  # Give the notification time to be processed async!

        self.assertEquals(obs.dummy, message)


if __name__ == u'__main__':
    unittest.main()
