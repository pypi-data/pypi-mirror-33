import datetime
from royal_mail_rest_api.tools import RoyalMailBody
from royal_mail_rest_api.shipping import ShippingApi
from royal_mail_rest_api.tracking import TrackingApi
from royal_mail_rest_api.errors import RoyalMailError
from royal_mail_rest_api.get_credentials import return_credentials

if __name__ == '__main__':
    # Get our API credentials (from credentials.ini)
    creds = return_credentials()

    # make some nice easy to read variables for authenticating with
    CLIENT_ID = creds['royal_mail']['CLIENT_ID']
    CLIENT_SECRET = creds['royal_mail']['CLIENT_SECRET']
    USERNAME = creds['royal_mail']['USERNAME']
    PASSWORD_HASHED = creds['royal_mail']['PASSWORD_HASHED']

    # Create a new delivery object to make our address etc with
    body = RoyalMailBody('Delivery')

    # Add our items to it
    body.add_ship_date(None)
    body.add_service_type('royal_mail_tracked')
    body.add_service_format('inland_large_letter')
    body.add_service_offering('royal_mail_tracked_24')
    body.add_service_enhancements('e-mail_notification')
    body.add_service_occurence()
    body.add_signature()
    body.customer_reference = 'D123456'
    body.department_reference = 'Q123456'
    body.sender_reference = 'A123456'
    body.add_items(1, 100, 'g')
    body.add_receipient_contact('Joe Bloggs', 'joe.bloggs@royalmail.com', None, '07970810000')
    body.add_receipient_address('Broadgate Circle', 'London', None, 'BH10 6JJ', country='GB', building_number='1',
                                address_line2='Add line 2', address_line3='Add line 3', building_name='My building')

    # Request our body to use to request a label from royal mail
    my_rm_body = body.return_domestic_body()


    # Create a shipping object, populate it with our credentials
    my_shipping = ShippingApi(CLIENT_ID, CLIENT_SECRET, USERNAME, PASSWORD_HASHED)
    # Request an authentication token
    my_shipping.get_token()
    # Post a shipping request
    try:
        post_shipping = my_shipping.post_domestic(my_rm_body)
    except RoyalMailError as e:
        print(e)
    # Store our tracking id for use.
    tracking_ref = post_shipping['completedShipments'][0]['shipmentItems'][0]['shipmentNumber']

    # Get a label ! this is base64 encoded
    label = my_shipping.put_shipment_label(tracking_ref)

    # Now lets change some info about the receipient
    body.add_receipient_contact('Alex Hellier', 'alex@me.com', 'Alex S Hellier', '123455')
    # And get our update body - this is slightly different from the original request
    new_data = body.return_domestic_update_body()
    # Request a change
    change_name = my_shipping.put_shipment(tracking_ref, new_data)
    # Request a new label
    new_label = my_shipping.put_shipment_label(tracking_ref)

    # Lets delete the post request
    delete_shipping = my_shipping.delete_shipment(tracking_ref)

    # If we have some labels to manifest - request it
    manifest_info = {'yourReference': '123'}
    try:
        manifest_data = my_shipping.post_manifest(manifest_info)
    # Get the manifest doumentation - note, you will need the maniefest number to get this
        manifest_label = my_shipping.put_manifest(manifest_batch_number=5)
    except Exception as e:
        # this will probably fail unless you change some details
        print(e)
    # Test we don't need a new token:

    my_shipping.get_token()
    # now change the self.token_created to be 5 hours ago
    my_shipping.token_created = datetime.datetime.now() - datetime.timedelta(hours=5)
    my_shipping.get_token()


    # Now, a period of time has passed, we can track those packages
    tracking_api = TrackingApi(CLIENT_ID, CLIENT_SECRET)
    try:
        test_tracking = tracking_api.summary(tracking_ref)
        print(test_tracking)
    except Exception as e:
        print(e)

    try:
        test_pod = tracking_api.proof_of_delivery(tracking_ref)
        print(test_pod)
    except Exception as e:
        print(e)

    try:
        history_tracking = tracking_api.history(tracking_ref)
        print(history_tracking)
    except Exception as e:
        print(e)
