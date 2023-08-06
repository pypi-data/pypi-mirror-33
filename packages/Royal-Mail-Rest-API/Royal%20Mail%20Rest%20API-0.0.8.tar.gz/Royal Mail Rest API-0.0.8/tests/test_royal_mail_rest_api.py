#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `royal_mail_rest_api` package."""
import pytest
import datetime
from royal_mail_rest_api.tools import RoyalMailBody


def test_add_services():
    body = RoyalMailBody('delivery')
    with pytest.raises(ValueError):
        assert body.add_service_format()
        assert body.add_service_type()
        assert body.add_service_offering()
    with pytest.raises(KeyError):
        assert body.add_service_format('does not exist')
        assert body.add_service_type('does not exist')
        assert body.add_service_offering('does not exist')

    body.add_service_format('inland_parcel')
    body.add_service_type('royal_mail_24')
    body.add_service_offering('royal_mail_tracked_24')

    assert body.service_format == 'P'
    assert body.service_type == '1'
    assert body.service_offering =='TPN'


def test_create_object():
    with pytest.raises(ValueError):
        body = RoyalMailBody('not_supported_value')

    body = RoyalMailBody('delivery')
    assert body.shipment_type == 'delivery'



def test_add_ship_date():
    body = RoyalMailBody('delivery')
    with pytest.raises(TypeError):
        body.add_ship_date('2018-01-28')
    # Test we get date out in format YYYY-mm-dd
    body.add_ship_date(datetime.datetime.today())
    assert body.shipping_date == datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%d')

