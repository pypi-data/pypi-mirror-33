7.2
---

* Buffer stdout in remote commands to fix performance issues with
  verbose buildpacks

7.1
---

* Fix https://github.com/yougov/vr.server/issues/2

7.0
---

* Changed the way blobs are serialized for hashing, now using
  JSON to serialize, enabling the test suite to pass on Python 3.
  Build and release hashes are likely to be invalidated by moving
  to this release. Although the implications aren't well-known,
  this change may cause old builds and releases not to match,
  which may lead to extra builds and releases.

6.11
----

* When doing builds, always set LANG=C.UTF-8 to avoid errors
  when the builder emits non-ascii.

6.9
---

* Clean StingRay pool if empty

6.8
---

* Don't swarm on inactive hosts
* Interpolate env environments mentioned in swarm config

6.7
---

* Don't try to remove a proc that is not actually running
* Fix procs scooping, to avoid cleaning build artifacts

6.6
---

* Improve navigation in UI by adding links to various resources
  (e.g. procs on host page)

6.5
---

* Incorporated `project skeleton from jaraco
  <https://github.com/jaraco/skeleton>`_
* Enabled automatic releases of tagged commits
* Tests now run on Travis-CI

6.4.4
-----

* Sort users and apps alphabetically in log page
* Dynamic proc filtering in dashboard

6.4.3
-----

* Fix https://github.com/yougov/velociraptor/issues/208

6.2.0
-----

* Run scooper task every 4 hours by default
* Optimise SQL queries by fetching related entities at once

6.1.0
-----

* Pin `requests` to avoid https://github.com/kennethreitz/requests/issues/3174
* Fix https://bitbucket.org/yougov/velociraptor/issues/165/navigating-back-after-dispatching-a-swarm
* Fix broken images link by not hardcoding static path
* Fix collection of proc names by using the correct line separator character

6.0.0
-----

* When resolving a repository scheme, the default command is now
  ``hg debugexpandscheme``, as that's the official command that
  is included with Mercurial 3.8.

  For compatibility with the previous behavior, set
  ``SCHEME_EXPAND_COMMAND=hg expand-scheme`` in the
  environment.

5.3.0
-----

* #201 Add support for NewRelic

5.0.1
-----

* Additional model garbage collection to troubleshoot memory leak in UI.

5.0.0
-----

* Removed dependency on Flower. Deployments should include
  the Flower dependency in their deployment if they wish
  to provide that service.
