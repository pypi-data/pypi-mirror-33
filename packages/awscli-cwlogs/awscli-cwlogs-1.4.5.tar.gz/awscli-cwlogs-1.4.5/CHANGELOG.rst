=========
CHANGELOG
=========
1.4.4
===
* Fix minor bug. Remove the message log, it will result in exception when there is non ASCII charactor

1.4.3
===
* Increase the default batch size to 1MB (from 32KB) and the default batch count to 10K (from 1K)
* Add loggroup placeholder support

1.4.2
===
* Upgrading to awscli 1.11.41
* Support configurable queue size

1.4.0
===
* Release this package to pypi under Amazon Software License.

1.3.3
===
* Support for Gzip http content encoding
* Support for dropin additional config files using --additional-configs-dir
* Upgrading to awscli 1.9.8

1.3.2
===
* Reuse same DB connection between threads

1.3.1
===
* Fix issue where bad input would give a 'no handlers could be found for logger' error for filter command
* Fix bug with encoding error in filter command for python 3

1.3.0
====
* New filter command for searching data in a log group.

1.2.2
====
* support large throughput put
* ignore archived/compressed files
* upgrade awscli to 1.7.21

1.2.1
====
* fix a bug that skips log lines during file rotation

1.2.0
====
* provide logging_config_file option to customize agent log

1.1.1
====
* Bug fix addressing a memory leak issue

1.1.0
=====
* upgrade AWSCLI to 1.4.4
* support custom fingerprint lines
* support custom new line start pattern
* fall back to timestamp of previous log event if needed
* make datetime_format optional and log process id
* add readme

1.0.1
=====
* upgrade AWSCLI to 1.3.22
* update some help docs
* log the exception when retry is needed

1.0.0
=====
+ add the initial AwsCWLogsPlugin
