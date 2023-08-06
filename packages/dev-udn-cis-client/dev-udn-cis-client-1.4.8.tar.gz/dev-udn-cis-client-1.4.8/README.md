
                              CIS client
---------------------------------------------------------------------

Consists of two main parts:
 - CLI tool for managing CIS, CS apps
 - python client library for managing CIS, CS apps

Current version can:
 - track content upload and jobs processing status

CLI tool usage:
    $ cis-client --help

    $ export CIS_CLIENT_AAA_HOST=https://aaa-dal.cdx-dev.unifieddeliverynetwork.net:7999
    $ export CIS_CLIENT_NORTH_HOST=http://cis-north.cdx-dev.udnapi.net
    $ export CIS_CLIENT_USERNAME=
    $ export CIS_CLIENT_PASSWORD=
    $ export CIS_CLIENT_BRAND_ID=udn
    $ export CIS_CLIENT_ACCOUNT_ID=1

    $ cis-client job_status --group-id=1
    $ cis-client job_status --path-list=new_dir/nested_dir,mydir/foo/bar
    $ cis-client job_status --path-list-file=/home/valera/content_list_file.txt --password=XXX

    $ cis-client upload --source-file-list=/home/valera/content_list_file.txt --protocol=aspera --password=XXX
    $ cis-client upload --source-file-list=/home/valera/content_list_file.txt --protocol=http --password=XXX

    Each argument like --password or --path-list can be specified via env.
    Env variables must be prefixed with CIS_CLIENT_ and name of argument specified with UPPERCASE and hyphens must be replaces with underscores.
    For example:
    password -> CIS_CLIENT_PASSWORD
    group-id -> CIS_CLIENT_GROUP_ID
    ...

Python Client Example:
    $ python
    >>> from cis_client.lib.cis_north import jobs_client
    >>> jobs_client.get_jobs("http://localhost:7999", "username", "secret", "http://127.0.0.1:8890", group_id=1)


Dev runner:
  $ pip install --editable .
  $ cis_client/run.py


Tests requirements:
 $ pip install pytest
 $ pip install pytest-mock
 $ pip3 install mock
Run tests:
 $ pytest
