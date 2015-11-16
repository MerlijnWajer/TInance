==========
Automation
==========

For monthly:

* Restrict database entries to a certain date?
* Tool should produce report(s) for a certain month, and produce a text
  representation, as well as html representation and latex
* Possibly the tool can be a makefile?

TODO for stats.py: Average payment for member should be based on members last payment only::

    member.last_payment / member_last_payment_months.
    (Be wary of no payments and wary of 0 months)


For invoices:

* Automate generating invoices with a jinja (latex) template as well
  (not strictly monthly related, but needs to be done too.)
  - make invoices/info_fields-number.txt -> invoices/invoice-number.pdf
  - also print email addr?

For yearly:

* Template for yearly report as well, using jinja and ledger.
