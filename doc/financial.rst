Techinc Financial administration
================================

We will start by introducing terminology and how the system works. It will later
on cover manipulating the database using command line tools and automated
processing of transactions; and finally gathering useful information.

What the system needs to do
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Database
~~~~~~~~

The database is SQLite3 and stored in ``tidb/db.db``.

Command line frontend
~~~~~~~~~~~~~~~~~~~~~


Bank imports
~~~~~~~~~~~~

One of the important aspects of the TechInc treasury is semi-automatically
processing payments made by members. This way the members will not forget to pay
for their membership and estimates can be made based on monthly income. This
document is supposed to aid the treasurer in using the financial system.

MT940 and identification
------------------------

MT940 is one of the formats used by banks. Our code is able to parse MT940 bank
exports - within reason; the MT940 format is quite terrible. We can succesfully
parse descriptions, amounts and dates. To identify members by the transactions
we typically require them to add the following to their payment description:

    MEMBERSHIP: <NICKNAME>

Checking for names or IBAN identification of a member is not enough; as
sometimes members will pay on behalf of other members (who cannot do bank
transfers), in which case just matching on an IBAN account would result in false
matches. Another case where matching on just IBAN is poor would be when a member
would pay to TechInc for a reason other than paying for membership. The payment
description is very important to make your life as TechInc treasurer simple, so
do ask members to add such a description, and preferrably make their payments
automated and recurring.

Parsing
-------

Parsing is done in two steps; the first step is the automated processing and
converting of the MT940 format to JSON. This step will try to find out which
transactions are payments by members. Once this automated step is complete, the
treasurer is required to manually verify that the tool did a proper job and
possible perform a few manual steps to process transactions previously not
recognised or by definition unrecognisable.

The file mt940/mt940.py can parse MT940 formats. It will also attempt to
recognise which member made what payment, within reason. It uses a (private)
members_strings.py file which maps certain payments to members based on simple
string searches. It will output payments recognised to stdout; whereas unknown
payments are output to stderr. Usage would be like this:

    $ python mt940.py MT940140331144020.STA  1>accept.json 2>reject.json

Where ``accept.json`` will now contain all the recognised payments, in
JSON format.
The ``reject.json`` file contains the other (not immediately) recognised
payments, also in JSON format.

The JSON format contains the following entries:

* nick: This is the nickname of the member
* date: The date of the payment
* amount: The amount paid in the transaction
* months: The amouth of months that was paid for in one go. This defaults to '1'
  and **is to be changed by the treasurer when required**.
* hash: This SHA256-hash is generated to be able to uniquely identify payments;
  this makes it possible to recognise if a payment was already processed, and
  either warn the treasurer or even ignore the payment all together.

An example ::

    {
        "hash": "b717ec481b3a84f1faa36c3344af2f70348b84ebd8ef1e471786c4100fa70e6c", 
        "months": 1, 
        "nick": "wizzup", 
        "amount": 42.0, 
        "date": "2014-01-02", 
        "desc": "/TRTP/SEPA OVERBOEKING/IBAN/NL28TRIO0XXXXXXXXX/BIC/TRIONL2U/NAME/M.B.W. WAJER/REMI/MEMBERSHIP WIZZUP/EREF/TRIODOS/NL/20140101/13XXXXXX"
    }

The accept and reject files
```````````````````````````

The accept and reject files contain payments recognised and not recognised,
respectively. The treasurer is **required to verify both files**; the
accept file for any months that need changing, and the reject file for any
transactions that were not recognised but are a membership payment. Once the
treasurer has identified payments in the reject file that need to processed, the
is encouraged to add remove the specific part of the JSON from the reject file
and place them in the accept file.

Optionally, if the treasurer is unsure about certain transactions, he can remove
them from either (or both) ``accept.json`` and ``reject.json`` and place them in
``todo.json``. **The todo.json file should not be removed until all the
transactions in there have been taken care of; either by processing them or
deeming them irrelevant.**

Once this manual labour is done, the end result should be:

* An ``accept.json`` file which contains all the transactions that are
  membership payments that need to be processed and added to the database.
* An ``reject.json`` file which contains transactions irrelevant to membership
  payments.
* Optionally a ``todo.json`` file **or payments that need to be processed at a later time.**

I will stress it once more, it is important to NOT remove the ``todo.json``
file unless you are sure it can be removed.

On recognising previous payments
````````````````````````````````

It may very happen that you process a MT940 file which contains previously
analysed transactions. Be it transactions that are already-processed membership
payments or transactions that were not relevant. The system gives you a way to
automatically discard both; as they are not relevant - because they have been
already processed or were already deemed irrelevant.

Transactions already processed will have their hash available in the database,
the import tool has the option to discard payments with an existing hash;
because they have already been taken care of.

Ignoring transactions previously deemed invalid is a slightly more work, at
least at this point. It requires you to **save the hashes from all your previous
(final) ``reject.json`` files.** This can be done as follows:

    $ mt940/filter_reject.sh reject.json >> reject_hashes_store

After which the import tool can be told to read the ``reject_hashes_store`` file
to discard any transactions that match one of the hashes found in there, with
the ``-R`` flag, (more on import.py later on the document) like so:

    $ python import.py -f accept.json -R mt940/hashes_reject

Importing accept.json data
--------------------------

A basic import looks as follows:

    $ python import.py -f accept.json

This will process the accept.json file and check for any errors. **Note that is
does not yet add the payments to the database!**. To actually import the data,
issue the following command (note the ``-i`` flag):

    $ python import.py -f accept.json -i

If you have worked on a ``todo.json``; you can pass ``todo.json`` as argument
with ``-f`` instead.

Importing, a recap
------------------

First, process the MT940 data:

    $ python mt940.py MT940140331144020.STA  1>accept.json 2>reject.json

Then, manually inspect and modify the ``accept.json``, ``reject.json`` and
optionally ``todo.json``. Finally, import it to the database:

    $ python import.py -f accept.json -i
