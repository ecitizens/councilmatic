from datetime import (date, datetime, timedelta)
from django.core import mail

from nose.tools import *
from mock import *

from main import feeds

from subscriptions.management.commands import sendfeedupdates
from subscriptions.management.commands import updatefeeds
from subscriptions.models import Subscriber

from phillyleg.models import LegFile


class SubscriptionFlowTesterMixin (object):

    def create_initial_content(self):
        raise NotImplementedError()

    def create_updated_content(self):
        raise NotImplementedError()

    def get_feed(self):
        raise NotImplementedError()

    def get_initial_dispatch_message(self):
        raise NotImplementedError()

    @istest
    def test_subscription_flow(self):
        LegFile.objects.all().delete()
        Subscriber.objects.all().delete()

        # First, let's make some content
        self.subscriber = subscriber = Subscriber.objects.create()
        self.create_initial_content()

        # Then, let's get the ContentFeed objects for this package.  One of them
        # should watch this content.
        feeds.library.clear()
        feeds.register_feeds()

        feed = self.get_feed()

        # Now we want a subscriber to subscribe to the feed.
        subscription = subscriber.subscribe(feed, library=feeds.library)

        # Assume that we last sent the subscription before the current items.
        subscription.last_sent = date(2011, 11, 11)
        subscription.save()

        # Now, update all the feeds dates/times and send out the updated content.
        update = updatefeeds.Command()
        update.handle()

        send = sendfeedupdates.Command()
        send.handle()

        # Check that we have a message to send.
        assert_equal(len(mail.outbox), 1)
        assert_equal(mail.outbox[0].subject[:19], 'Philly Councilmatic')
        assert_equal(mail.outbox[0].body, self.get_initial_dispatch_message())

        # Cool.  Clear the mailbox.
        del mail.outbox[:]

        # Now, if we update the feed times and send the updated content, there
        # should be nothing to send.
        update = updatefeeds.Command()
        update.handle()

        send = sendfeedupdates.Command()
        send.handle()

        assert_equal(len(mail.outbox), 0)

        # Put something else into the feed.
        self.create_updated_content()

        # Now, update all the feeds dates/times and send out the updated content.
        update = updatefeeds.Command()
        update.handle()

        send = sendfeedupdates.Command()
        send.handle()

        assert_equal(len(mail.outbox), 1)

        # ... and at the end, return to a clean state.
        feeds.library.clear()


class TestNewLegislationFeedDispatching(SubscriptionFlowTesterMixin):
    def create_initial_content(self):
        LegFile.objects.create(key=1, id='a', title="first", intro_date=date(2011, 12, 13), type="Bill")
        LegFile.objects.create(key=2, id='b', title="second", intro_date=date(2011, 12, 13), type="Bill")
        LegFile.objects.create(key=3, id='c', title="third", intro_date=date(2011, 12, 13), type="Bill")

    def create_updated_content(self):
        LegFile.objects.create(key=4, id='d', title="fourth", intro_date=date(2012, 2, 4), type="Bill")

    def get_feed(self):
        return feeds.NewLegislationFeed()

    def get_initial_dispatch_message(self):
        return ('Philadelphia Councilmatic!\n==========================\n\nY'
                'ou are subscribed to the following feeds:\n\n\n* bookmarked'
                ' content\n\n* newly introduced legislation\n\n\n\n---------'
                '-----------------------------------------------------------'
                '------------\n\nBILL a\n\nTitle: first\n\nMore at http://ex'
                'ample.com/legislation/1\n\n\n------------------------------'
                '--------------------------------------------------\n\nBILL '
                'b\n\nTitle: second\n\nMore at http://example.com/legislatio'
                'n/2\n\n\n--------------------------------------------------'
                '------------------------------\n\nBILL c\n\nTitle: third\n'
                '\nMore at http://example.com/legislation/3\n\n')


class TestNewLegislationFeedDispatching(SubscriptionFlowTesterMixin):
    def create_initial_content(self):
        LegFile.objects.create(key=1, id='a', title="first", intro_date=date(2011, 12, 13), type="Bill")
        LegFile.objects.create(key=2, id='b', title="second", intro_date=date(2011, 12, 13), type="Bill")
        LegFile.objects.create(key=3, id='c', title="third", intro_date=date(2011, 12, 13), type="Bill")

    def create_updated_content(self):
        LegFile.objects.create(key=4, id='d', title="fourth", intro_date=date(2012, 2, 4), type="Bill")

    def get_feed(self):
        return feeds.NewLegislationFeed()

    def get_initial_dispatch_message(self):
        return ('Philadelphia Councilmatic!\n==========================\n\nY'
                'ou are subscribed to the following feeds:\n\n\n* bookmarked'
                ' content\n\n* newly introduced legislation\n\n\n\n---------'
                '-----------------------------------------------------------'
                '------------\n\nBILL a\n\nTitle: first\n\nMore at http://ex'
                'ample.com/legislation/1\n\n\n------------------------------'
                '--------------------------------------------------\n\nBILL '
                'b\n\nTitle: second\n\nMore at http://example.com/legislatio'
                'n/2\n\n\n--------------------------------------------------'
                '------------------------------\n\nBILL c\n\nTitle: third\n'
                '\nMore at http://example.com/legislation/3\n\n')
