# -*- coding: utf-8 -*-
# Description: Implements an Observable class that can be added
#              simply to another class.
#              https://en.wikipedia.org/wiki/Observer_pattern
# Author: Hywel Thomas

import logging_helper
from pprint import pformat
from .queue_processor import QueueProcessor

logging = logging_helper.setup_logging()


class ObserverError(Exception):
    pass


class Observable(QueueProcessor):

    def __initialise_if_required(self):

        try:
            self.observers

        except AttributeError:
            # First observer, initialise
            #self.start_queue_processor()  # Disabled until uiutil is thread safe

            self.observers = []
            self.notified_kwargs = {}

    def _queue_processor_worker(self,
                                **params):

        try:
            self._perform_notification(**params)

        except Exception as err:
            logging.error(u'Something went wrong while performing notification!')
            logging.exception(err)

    def register_observer(self,
                          observer):

        logging.debug(u'Register: {o} to {n}'.format(o=observer.__class__,
                                                     n=self.__class__))

        self.__initialise_if_required()

        try:
            _ = observer.notification

        except AttributeError:
            raise ObserverError(u'{observer} does not have a notification method.'.format(observer=type(observer)))

        try:
            _ = observer.observing

        except AttributeError:
            raise ObserverError(u'{observer} does not inherit Observer class.'.format(observer=type(observer)))

        self._initial_notification(observer)
        self.observers.append(observer)
        observer.observing.append(self)

    def unregister_observer(self,
                            observer):

        logging.debug(u'Unregister: {o} from {n}'.format(o=observer.__class__,
                                                         n=self.__class__))

        self.__initialise_if_required()

        try:
            self.observers.remove(observer)

        except ValueError:
            logging.error(u'{observer} is not a registered observer of {i}!'.format(observer=type(observer),
                                                                                    i=type(self)))

        try:
            observer.observing.remove(self)

        except ValueError:
            logging.error(u'{observer} is not observing {i}!'.format(observer=type(observer),
                                                                     i=type(self)))

    def unregister_observers(self):

        """ Unregisters all observers in one go! """

        self.__initialise_if_required()

        for observer in self.observers[:]:  # Slice notation required otherwise some items get missed out.
            self.unregister_observer(observer)

    def _initial_notification(self,
                              observer):

        """ Override to perform a custom initial notify.

        If not overridden this will pass previous status of all params passed
        for this object.

        :return:
        """

        kwargs = self.notified_kwargs

        logging.debug(u'Initial Notify kwargs:\n'
                      u'{kwargs}'.format(kwargs=pformat(kwargs)))

        kwargs[u'observer'] = observer
        #self.queue.put(kwargs)  # Disabled until uiutil is thread safe
        self._perform_notification(**kwargs)

    def notify_observers(self,
                         **kwargs):

        self.__initialise_if_required()

        self.notified_kwargs.update(kwargs)

        logging.debug(u'Notify kwargs:\n'
                      u'{kwargs}'.format(kwargs=pformat(kwargs)))

        for observer in self.observers:
            if self in observer.observing:
                kwargs[u'observer'] = observer
                #self.queue.put(kwargs)  # Disabled until uiutil is thread safe
                self._perform_notification(**kwargs)

            else:
                logging.warning(u'Cancelling notification to {observer} as '
                                u'it does not appear to be observing {i}'.format(observer=type(observer),
                                                                                 i=type(self)))

    def _perform_notification(self,
                              observer,
                              **kwargs):

        # Add notifier to kwargs
        kwargs[u'notifier'] = self

        try:
            _ = observer.notification

        except AttributeError:
            logging.warning(u'Observer does not inherit Observer class, '
                            u'not performing notification: {o}'.format(o=type(observer)))

        else:
            try:
                observer.notification(**kwargs)

            except Exception as err:
                # Catch and log exceptions
                # No longer raising them further as a failed notification should not affect further running.
                logging.exception(err)

                # Maybe remove the observer if an exception has occurred?

    @property
    def observer_count(self):
        try:
            return len(self.observers)

        except AttributeError:
            return 0

    @property
    def observed(self):
        return self.observer_count != 0

    def observed_by(self,
                    observer):
        try:
            return observer in self.observers

        except AttributeError:
            return False


class Observer(object):

    NOTIFIER_KEY = u'notifier'

    @property
    def observing(self):
        try:
            self._observing

        except AttributeError:
            self._observing = []

        return self._observing

    def unregister_observables(self):

        """ Unregister from everything we are observing! """

        for observer in self.observing[:]:  # Slice notation required otherwise some items get missed out.
            observer.unregister_observer(self)

    def notification(self,
                     **kwargs):
        """ Override to perform an actions on notification from observable. """
        pass


class ObservableMixIn(Observable):
    pass


class ObserverMixIn(Observer):
    pass


class ObservableObserverMixIn(ObservableMixIn,
                              ObserverMixIn):
    pass
