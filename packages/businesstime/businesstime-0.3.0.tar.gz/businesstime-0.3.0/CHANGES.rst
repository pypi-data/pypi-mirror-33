0.3.0
=====
* Fix a bug (#25) where holidays were not properly detected when later dates were tested before earlier ones, thanks @agans
* Fix a bug (#13) where time deltas were calculated incorrectly when both start and end times are after business hours, thanks @airsource
* `businesstime_hours` now returns a `timedelta` rather than a numeric value (#23), thanks @naes17
* `businesstimedelta` now returns negative timedeltas when the start time is after the end time (#19), thanks @jeremyklein
* Add 2017-2018 public holidays for Queensland/Brisbane Australia (#17), thanks @danc86

0.2.1
=====
* Fix broken pypi package (#14), thanks @tarkatronic

0.2.0
=====
* Change package layout: country-specific holidays are stored in files named w/ their ISO 3166-1 alpha-3 country codes
* Add 2013-2016 public holidays for Queensland/Brisbane Australia (#11), from @danc86
* Fix AttributeError when no holidays are specified (#10), from @danc86

0.1.6
=====
* Handle US federal holidays that fall on the weekend but are observed on Friday/Monday (#8)

0.1.5
=====
* Fixed a bug (#7) where a datetime after business hours and a datetime during business hours were handled incorrectly

0.1.4
=====
* Fixed a bug (#6) where two datetimes on the same day but before business hours were handled incorrectly

0.1.3
=====
* Fixed a bug (#3) where the first instant of a business day was not considered part of that day

0.1.2
=====
* Fix changelog

0.1.1
=====
* Fix pypi package

0.1.0
=====
* Public Release
