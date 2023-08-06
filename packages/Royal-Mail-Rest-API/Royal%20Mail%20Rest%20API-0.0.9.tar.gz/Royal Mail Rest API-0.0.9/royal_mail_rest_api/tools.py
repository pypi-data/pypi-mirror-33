import datetime
from royal_mail_rest_api.errors import *
from collections import namedtuple

valid_service = namedtuple('valid_service',
                           'serviceType serviceOffering serviceFormat enhancementType signatureTracked safePlace')


class RoyalMailBody:

    service_formats = {
        'inland_large_letter': 'F',
        'inland_letter': 'L',
        'inland_format_not_applicable': 'N',
        'inland_parcel': 'P',
        'international_parcel': 'E',
        'international_large_letter': 'G',
        'international_format_not_applicable': 'N',
        'international_letter': 'P'
    }

    service_types = {
        'royal_mail_24': '1',
        'Royal Mail 48': '2',
        'special_delivery': 'D',
        'BFPO': 'H',
        'international': 'I',
        'tracked_returns': 'R',
        'royal_mail_tracked': 'T'
    }

    service_offerings = {
        "royal_mail_24_48": "CRL",
        "intl_bus_parcels_zero_sort_hi_vol_priority_i": "DE1",
        "intl_bus_parcels_zero_sort_hi_vol_economy_": "DE3",
        "intl_bus_parcels_zero_srt_lo_vol_priority_": "DE4",
        "intl_bus_parcels_zero_srt_lo_vol_economy_": "DE6",
        "intl_bus_mail_l_ltr_ctry_srt_hi_vol_priority_": "DG1",
        "intl_bus_mail_l_ltr_ctry_srt_hi_vol_economy_": "DG3",
        "intl_bus_mail_l_ltr_ctry_srt_lo_vol_priority_": "DG4",
        "intl_bus_mail_l_ltr_ctry_srt_lo_vol_economy_": "DG6",
        "royal_mail_24_sort8_ll_flat_rate": "FS1",
        "royal_mail_48_sort8_ll_flat_rate": "FS2",
        "intl_bus_parcels_zone_sort_priority_": "IE1",
        "intl_bus_parcels_zone_sort_economy": "IE3",
        "intl_bus_mail_lrg_ltr_zone_sort_pri": "IG1",
        "intl_bus_mail_lrg_ltr_zone_sort_economy": "IG3",
        "intl_bus_mail_lrg_ltr_zone_srt_pri_mch": "IG4",
        "intl_bus_mail_l_ltr_zone_srt_economy_mch_": "IG6",
        "intl_bus_parcels_print_direct_priority": "MB1",
        "intl_bus_parcels_print_direct_standard": "MB2",
        "intl_bus_parcels_print_direct_economy": "MB3",
        "intl_bus_parcels_signed_extra_comp_ctry": "MP0",
        "intl_bus_parcels_tracked": "MP1",
        "intl_bus_parcels_tracked_extra_comp": "MP4",
        "intl_bus_parcels_signed": "MP5",
        "intl_bus_parcels_signed_extra_comp": "MP6",
        "intl_bus_parcels_tracked_country_priced": "MP7",
        "intl_bus_parcels_tracked_extra_comp_ctry": "MP8",
        "intl_bus_parcels_signed_country_priced": "MP9",
        "intl_bus_parcels_tracked_and_signed": "MTA",
        "intl_bus_parcels_tracked_signed_xtr_comp": "MTB",
        "intl_bus_mail_tracked_and_signed": "MTC",
        "intl_bus_mail_tracked_and_signed_xtr_comp": "MTD",
        "intl_bus_parcels_tracked_and_signed__ctry": "MTE",
        "intl_bus_parcel_track&sign_xtr_cmp_ctry": "MTF",
        "intl_bus_mail_tracked_and_signed_country": "MTG",
        "intl_bus_mail_track_and_sign_xtr_comp_ctry": "MTH",
        "intl_bus_mail_tracked": "MTI",
        "intl_bus_mail_tracked_extra_comp": "MTJ",
        "intl_bus_mail_tracked_country_priced": "MTK",
        "intl_bus_mail_tracked_extra_comp_ctry": "MTL",
        "intl_bus_mail_signed": "MTM",
        "intl_bus_mail_signed_extra_comp": "MTN",
        "intl_bus_mail_signed_country_priced": "MTO",
        "intl_bus_mail_signed_extra_comp_country": "MTP",
        "intl_bus_parcels_zone_sort_plus_priority": "MTQ",
        "intl_bus_parcels_zone_srt_plus_economy": "MTS",
        "intl_standard_on_account": "OLA",
        "intl_economy_on_account": "OLS",
        "international_signed_on_account": "OSA",
        "intl_signed_on_account_extra_comp": "OSB",
        "international_tracked_on_account": "OTA",
        "intl_tracked_on_account_extra_comp": "OTB",
        "international_tracked_and_signed_on_acct": "OTC",
        "intl_tracked_and_signed_on_acct_extra_comp": "OTD",
        "intl_bus_mail_mixed_zone_sort_priority": "OZ1",
        "intl_bus_mail_mixed_zone_sort_economy": "OZ3",
        "intl_bus_mail_mixed_zone_sort_pri_mch": "OZ4",
        "intl_bus_mail_mixed_zone_srt_economy_mch": "OZ6",
        "royal_mail_48_ll_flat_rate": "PK0",
        "royal_mail_24_sort8_p_flat_rate": "PK1",
        "royal_mail_48_sort8_p_flat_rate": "PK2",
        "royal_mail_24_sort8_llp_daily_rate": "PK3",
        "royal_mail_48_sort8_llp_daily_rate": "PK4",
        "royal_mail_24_ll_flat_rate": "PK9",
        "royal_mail_24_48_p_flat_rate": "PPF",
        "intl_bus_parcels_max_sort_economy": "PS0",
        "intl_bus_parcels_max_sort_standard": "PSC",
        "intl_bus_parcels_max_sort_priority": "PS9",
        "intl_bus_mail_lrg_ltr_max_sort_economy": "PS8",
        "intl_bus_mail_lrg_ltr_max_sort_standard": "PSB",
        "intl_bus_mail_lrg_ltr_max_sort_priority": "PS7",
        "royal_mail_48_sort8_p_daily_rate": "RM0",
        "royal_mail_24_ll_daily_rate": "RM1",
        "royal_mail_24_p_daily_rate": "RM2",
        "royal_mail_48_ll_daily_rate": "RM3",
        "royal_mail_48_p_daily_rate": "RM4",
        "royal_mail_24_p_flat_rate": "RM5",
        "royal_mail_48_p_flat_rate": "RM6",
        "royal_mail_24_sort8_ll_daily_rate": "RM7",
        "royal_mail_24_sort8_p_daily_rate": "RM8",
        "royal_mail_48_sort8_ll_daily_rate": "RM9",
        "sd_guaranteed_by_1pm": "SD1",
        "sd_guaranteed_by_1pm_1000": "SD2",
        "sd_guaranteed_by_1pm_2500": "SD3",
        "sd_guaranteed_by_9am": "SD4",
        "sd_guaranteed_by_9am_1000": "SD5",
        "sd_guaranteed_by_9am_2500": "SD6",
        "1st_and_2nd_class_account_mail": "STL",
        "royal_mail_tracked_48_hv": "TPL",
        "royal_mail_tracked_24_hv": "TPM",
        "royal_mail_tracked_24": "TPN",
        "royal_mail_tracked_48": "TPS",
        "royal_mail_tracked_48_lbt_hv": "TRL",
        "royal_mail_tracked_24_lbt_hv": "TRM",
        "royal_mail_tracked_24_lbt": "TRN",
        "royal_mail_tracked_48_lbt": "TRS",
        "royal_mail_tracked_returns_24": "TSN",
        "royal_mail_tracked_returns_48": "TSS",
        "intl_bus_parcels_zero_sort_priority": "WE1",
        "intl_bus_parcels_zero_sort_economy": "WE3",
        "intl_bus_mail_lrg_ltr_zero_srt_priority": "WG1",
        "intl_bus_mail_lrg_ltr_zero_sort_economy": "WG3",
        "intl_bus_mail_lrg_ltr_zero_srt_pri_mch": "WG4",
        "intl_bus_mail_l_ltr_zero_srt_economy_mch": "WG6",
        "intl_bus_mail_mixed_zero_sort_priority": "WW1",
        "intl_bus_mail_mixed_zero_sort_economy": "WW3",
        "intl_bus_mail_mixed_zero_sort_pri_mch": "WW4",
        "intl_bus_mail_mixd_zero_srt_economy_mch": "WW6",
        "intl_bus_mail_mixed_zero_sort_premium": "ZC1",
    }

    service_enhancements = {
        "loss_1000": "1",
        "loss_2500": "2",
        "loss_5000": "3",
        "loss_7500": "4",
        "loss_10000": "5",
        "recorded": "6",
        "loss_750": "11",
        "signature": "12",
        "sms_notification": "13",
        "e-mail_notification": "14",
        "safeplace": "15",
        "sms_and_e-mail_notification": "16",
        "local_collect": "22",
        "saturday_guaranteed": "24",
    }

    def __init__(self, shipment_type):
        self.receipient = None
        self.address = None
        self.service = None
        self.shipping_date = None
        self._check_ship_type(shipment_type)
        self.sender_reference = None
        self.department_reference = None
        self.customer_reference = None
        self.items = []
        self.item_count = len(self.items)
        self.safe_place = None
        self.enhancements = []

    def return_domestic_body(self):
        """
        build domestic body from items
        :return:
        """

        domestic_body = {
            'shipmentType': self.shipment_type,
            'service': self._add_service(),
            'shippingDate': self.shipping_date,
            'items': self.items,
            'recipientContact': self.receipient,
            'recipientAddress': self.address,
            'senderReference': self.sender_reference,
            'departmentReference': self.department_reference,
            'customerReference': self.customer_reference,
            'safePlace': self.safe_place
        }

        return domestic_body

    def return_domestic_update_body(self):
        """
        build domestic body from items
        :return:
        """

        domestic_body = {
            'service': self.service,
            'shippingDate': self.shipping_date,
            'recipientContact': self.receipient,
            'recipientAddress': self.address,
            'senderReference': self.sender_reference,
            'departmentReference': self.department_reference,
            'customerReference': self.customer_reference,
            'safePlace': self.safe_place
        }

        return domestic_body

    @staticmethod
    def remove_none_values(iterable):
        """
        take out values of None by removing the key
        :param iterable:
        :return: dictionary
        """

        new_dict = {k: v for k, v in iterable.items() if v is not None}

        return new_dict

    def _check_ship_type(self, shipment_type):
        """
        Check that the shipment type is valid (currently only delivery)
        :param shipment_type:
        :return:
        """
        if shipment_type.lower() != 'delivery':
            # TODO: Find out the other options here!
            raise ValueError('Sorry, only delivery supported at the moment')
        else:
            self.shipment_type = shipment_type.lower()

    def add_ship_date(self, date_obj=None):
        """
        take a datetime object and format it to royal mails Y-m-d format
        :param date_obj:
        :return:
        """

        if date_obj is None:
            date_obj = datetime.datetime.today()
        if isinstance(date_obj, datetime.datetime):
            self.shipping_date = datetime.datetime.strftime(date_obj, '%Y-%m-%d')
        else:
            raise (TypeError('Sorry, need a datetime object'))

    def _add_service(self):
        """
        create our service block from already added inputs
        :return:
        """
        service = {
            "format": self.service_format,
            "occurrence": self.service_occurence,
            "offering": self.service_offering,
            "type": self.service_type,
            "signature": self.signature,
            "enhancements": self.enhancements
        }

        return service

    def add_service_format(self, format=None):
        """
        add a valid service format using our friendly names
        :param format:
        :return:
        """
        if format is None:
            raise (ValueError('No service format selected'))
        if format not in self.service_formats:
            raise (KeyError('Invalid service format'))
        self.service_format = self.service_formats[format]

    def add_service_type(self, service_type=None):

        """
        add a valid service type using our friendly names
        :param service_type:
        :return:
        """

        if service_type is None:
            raise (ValueError('no service type selected'))

        if service_type not in self.service_types:
            raise (KeyError('Invalid service type'))
        self.service_type = self.service_types[service_type]

    def add_service_offering(self, service_offering=None):
        """
        add a valid service offering using our friendly names
        :param service_offering:
        :return:
        """

        if service_offering is None:
            raise (ValueError('No service type selected'))
        if service_offering not in self.service_offerings:
            raise (KeyError('Invalid service type'))
        self.service_offering = self.service_offerings[service_offering]

    def add_service_occurence(self):
        # TODO - what is this, can't find anything in the docs
        self.service_occurence = 1

    def add_signature(self, signature=False):
        """
        Do we want a signature on delivery
        :param signature:
        :return:
        """
        if isinstance(signature, bool):
            self.signature = signature
        else:
            raise (TypeError('Must be a boolean, True or False'))

    def add_service_enhancements(self, enhancement):
        """
        add a single service enhancement, can be called multiple times to append required items
        :param enhancement:
        :return:
        """
        if enhancement is None:
            raise (ValueError('No Enhancement Selected'))
        if enhancement not in self.service_enhancements:
            raise (KeyError('Not in service_enhancements'))
        self.enhancements.append(self.service_enhancements[enhancement])

    def add_receipient_contact(self, name, email, complementary_name=None, telephone=None):
        """
        Add the name and contact of who this is being sent to
        :param name:
        :param email:
        :param complementary_name:
        :param telephone:
        :return:
        """
        receipient = {
            "name": name,
            "complementaryName": complementary_name,
            "telephoneNumber": telephone,
            "email": email
        }

        # receipient = self.remove_none_values(receipient)
        self.receipient = receipient

    def add_items(self, number, weight, unit_of_measure):
        """
        Add items- currently only a single item
        :param number:
        :param weight:
        :param unit_of_measure:
        :return:
        """
        items = [{
            "count": number,
            "weight": {
                "unitOfMeasure": unit_of_measure,
                "value": weight
            },
        }]

        self.items = items

    def add_receipient_address(self, address_line1, post_town, county, postcode, country, building_name=None,
                               building_number=None, address_line2=None, address_line3=None):
        """
        Add address of receipient
        :param address_line1:
        :param post_town:
        :param county:
        :param postcode:
        :param country:
        :param building_name:
        :param building_number:
        :param address_line2:
        :param address_line3:
        :return:
        """
        address = {
            "buildingName": building_name,
            "buildingNumber": building_number,
            "addressLine1": address_line1,
            "addressLine2": address_line2,
            "addressLine3": address_line3,
            "postTown": post_town,
            "county": county,
            "postCode": postcode,
            "country": country
        }

        # address = self.remove_none_values(address)
        self.address = address

