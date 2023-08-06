Example Shipping object from Royal Mail
=======================================

.. code-block:: json

    {
    "shipmentType":"Delivery",
     "service":{
                "format":"P",
                "occurrence":"1",
                "offering":"TPN",
                "type":"T",
                "signature":"true",
                "enhancements":["14"

                ]
             },
    "shippingDate":"2017-09-25",
    "items":[
       {
         "count":1,
         "weight":{
                       "unitOfMeasure":"g",
                       "value":100
          }
        }
      ],
      "recipientContact":{
         "name":"Joe Bloggs",
         "complementaryName":"null",

         "email":"joe.bloggs@royalmail.com"
         },

       "recipientAddress":{
         "buildingName":"Cable and Engineering Limited",
         "buildingNumber":"1",
         "addressLine1":"Broadgate Circle",
         "addressLine2":"Address line 2",
         "addressLine3":"Address Line 3",
         "postTown":"London",
         "country":"GB",
         "postCode":"EC1A 1BB"
        },
      "senderReference":"Senders Ref",
      "departmentReference":"Dept Ref",
      "customerReference":"Do not use",
      "safePlace":"null"
    }
