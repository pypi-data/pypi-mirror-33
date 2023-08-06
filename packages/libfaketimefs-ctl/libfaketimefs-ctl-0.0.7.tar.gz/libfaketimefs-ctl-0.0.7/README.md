# libfaketimefs-ctl

This tool is used to control [libfaketimefs](https://github.com/claranet/libfaketimefs) across multiple servers. It uses DynamoDB for global state storage.

## Setup

1. Ensure that AWS credentials and `AWS_DEFAULT_REGION` are set using environment variables or instance credentials.
2. Create a DynamoDB table as per the example in the `terraform` directory.
2. Install using pip:

```shell
pip install libfaketimefs-ctl
```

## Usage

There are 2 types of operations available:

* Client operations (send commands)
* Server operations (receive commands)

Operations require a `--table` argument to specify the DynamoDB table. Actions performed by client operations will be seen by all servers using the same table.

### Client operations

Query the table and print information in JSON format.

```shell
$ libfaketimefs-ctl --table $DYNAMODB_TABLE --query
```

Send a command to jump to a specific date or datetime.

```shell
$ libfaketimefs-ctl --table $DYNAMODB_TABLE --jump now
$ libfaketimefs-ctl --table $DYNAMODB_TABLE --jump 2018-03-27
$ libfaketimefs-ctl --table $DYNAMODB_TABLE --jump "2018-04-12 16:09:57"
```

Send a command to fast forward to a specific date or datetime. The final number is used as the rate - the number of fake seconds that should pass for each real second that passes. After it has finished fast forwarding, the fake time will progress at normal speed.

```shell
$ libfaketimefs-ctl --table $DYNAMODB_TABLE --ff "2018-03-27 3"
$ libfaketimefs-ctl --table $DYNAMODB_TABLE --ff "2018-03-27 16:09:57 30"
```

Send a command to stop fast forwarding.

```shell
$ libfaketimefs-ctl --table $DYNAMODB_TABLE --stop
```

### Server operations

Watch the table for commands and write them to the libfaketimefs `/control` file.

```shell
$ libfaketimefs-ctl --table $DYNAMODB_TABLE --out /run/libfaketimefs/control
```
