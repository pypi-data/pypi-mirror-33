This module adds a workflow to approve page modification and show the approved
version by default.

Scenario
========

* Set a valid email address on the company settings.
* Create a new page category and set an approver group. Make sure users
  belonging to that group have valid email addresses.
* Create a new page and choose the previously created category.
* A notification is sent to the group with a link to the page history to
  review.
* Depending on the review, the page history is approved or not.
* Users reading the page see the last approved version.


