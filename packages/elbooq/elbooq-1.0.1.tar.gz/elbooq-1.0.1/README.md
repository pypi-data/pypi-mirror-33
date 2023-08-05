
Overview
============

Introduction
------------

elbooq supports diverse ways of integration using directly exposing REST service, elbooq payment library or deploying elbooq application for java technology. For REST service, we have included samples for **JAVA**, .**NET**, **PHP** and **Python**.

How does it work?
-----------------

We have developed a REST service called “`**initPayment**`”. It allows merchant to pay through elbooq payment gateway or KNET payment gateway. The merchant can initialize service with preferred payment option and based on this a secure payment URL will be retrieved to redirect buyer to elbooq landing page or KNET landing page. 

Also, you can request both gateways’ URLs in case you need to give more options to the buyer.

In addition, there is another REST service called “**`checkPayment`**”. This allows merchant to check if the payment is success against merchant order/invoice number mapped to merchant transaction. 

elbooq Payment Gateway Process
------------------------------

![](https://www.elbooq.net/media/filer_public_thumbnails/filer_public/12/c1/12c18487-d3d8-4040-a412-e1a911cb4953/elbooq_payment_gateway.png__2696x648_q85_subsampling-2.png)

* * *


