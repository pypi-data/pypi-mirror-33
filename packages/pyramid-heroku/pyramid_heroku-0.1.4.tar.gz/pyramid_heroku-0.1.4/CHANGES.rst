=======
Changes
=======

0.1.4
-----

* Fix return value in migrate.shell. `subprocess.check_output` changed in
  python 3.6 and is now returning byte and not str.
  [karantan]

0.1.3
-----

* Provided default values for migrate.py - https://github.com/niteoweb/pyramid_heroku/issues/2
  [enkidulan]

0.1.2
-----

* The request.client_addr cannot be set directly, so we need to go around.
  [zupo]


0.1.1
-----

* Fix tween paths.
  [zupo]


0.1
---

* Initial release.
  [dz0ny, zupo]

