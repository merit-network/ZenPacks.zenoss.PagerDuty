=========================
ZenPacks.zenoss.PagerDuty
=========================

.. contents::
    :depth: 3

About
-----
This ZenPack extends Zenoss by providing a new PagerDuty Notification type
to send Zenoss events to PagerDuty Services via Events API v2.

This ZenPack builds upon and replaces ZenPacks.PagerDuty.APINotification


Prerequisites
-------------

==================  ==========================================================
Prerequisite        Restriction
==================  ==========================================================
Product             Zenoss 4.2.5 or higher
Required ZenPacks   None
Other dependencies  None
==================  ==========================================================


ZenPack Installation / Removal
------------------------------

Install or remove this ZenPack following the instructions in the Zenoss
Resource Manager Admin Guide matching your Zenoss RM version.

Upgrading from ZenPacks.PagerDuty.APINotification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If upgrading from the older ZenPacks.PagerDuty.APINotification ZenPack,
then the prior ZenPack needs to be completely removed prior to installation.
This includes all existing PagerDuty Notifications. The following steps are
recommended based on user testing.

* Pre Maintenance

  * Create a new v2 API Key on the PagerDuty site and store for later
    (https://support.pagerduty.com/v1/docs/using-the-api#section-generating-an-api-key)
  * Create a new Events API v2 Integration on the PagerDuty Services that will
    be used.

* Uninstall

  * Create a snapshot of Zenoss.resmgr
  * Remove any PagerDuty Notifications (note the settings for adding them back)
  * Uninstall the prior ZenPack (e.g., `serviced service run zope
    zenpack-manager uninstall ZenPacks.PagerDuty.APINotification`)
  * Stop and restart all Zenoss Services, including zproxy (Infrastructure can stay up)

* Install

  * Install the new ZenPack (e.g., `serviced service run zope zenpack-manager
    install ZenPacks.zenoss.PagerDuty-2.0.2-py2.7.egg`)
  * Stop and restart all Zenoss Services, including zproxy (Infrastructure can stay up)

* Configure

  * Configure Zenoss as below in 'Usage'

* Troubleshooting

  * A lot of changes are in the JavaScript files and caching may cause an
    issue - be sure to clear your browser's cache and reload to make sure the
    most current files are used.
  * If you're unable to save the new API Access Key and the textboxes seem
    small or you are seeing an infinite loading on the Notification window,
    stop all Zenoss services including Infrastructure services and start them
    back up. If this does not resolve the issue, you may need to roll back or
    retry the install.


Usage
-----

* **Configure PagerDuty**

  * API Key

    In order for PagerDuty to work with Zenoss an API key should be obtained.
    In the PagerDuty Dashboard go to Configuration->API access->Create API Key.
    If you are presented with an option, choose "v2."

  * Service Integrations

    Create an integration of type "Events API v2" for all necessary services.

* **Configure Zenoss**

  * Configure API Key

    Go to Advanced -> PagerDuty. Enter your PagerDuty subdomain & API key
    and click "Apply". A list of Services available in PagerDuty should display.

  * Configure Notifications

    Creating PagerDuty Notifications, the following properties can be edited
    in the Notification content tab:

    ===============  ==========================================================
    Title            Description
    ===============  ==========================================================
    Service          PagerDuty Service to send events to
    Service API Key  The API Key for the PagerDuty Service you want to alert
    Description      Text that will appear in the incident's log associated with this event
    ===============  ==========================================================


Changes
-------

Release 2.0.2

- Fixes

  * Prefer the v2 integration if v1 integration is also defined on the service.

Release 2.0.1

- Fixes

  * API Details disappearing from UI

Release 2.0.0

- Features

  * Switch to PagerDuty API v2
