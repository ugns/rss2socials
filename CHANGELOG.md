# CHANGELOG

<!-- version list -->

## v1.1.3 (2025-07-09)

### Bug Fixes

- **package**: Update dependency openai to v1.93.3
  ([#12](https://github.com/ugns/rss2socials/pull/12),
  [`2df03a2`](https://github.com/ugns/rss2socials/commit/2df03a2d134b3c4c7732e4911d26e4f6decd8515))


## v1.1.2 (2025-07-08)

### Bug Fixes

- **package**: Update dependency openai to v1.93.2
  ([#11](https://github.com/ugns/rss2socials/pull/11),
  [`da244e1`](https://github.com/ugns/rss2socials/commit/da244e1c051b09d71acb649aa4f7513af55bd1ad))


## v1.1.1 (2025-07-07)

### Bug Fixes

- **package**: Update dependency openai to v1.93.1
  ([#10](https://github.com/ugns/rss2socials/pull/10),
  [`1ee731b`](https://github.com/ugns/rss2socials/commit/1ee731b4393c49b528786e7282486f5debe153cb))


## v1.1.0 (2025-07-01)

### Bug Fixes

- Correct author email format and update project metadata in pyproject.toml
  ([#9](https://github.com/ugns/rss2socials/pull/9),
  [`92b867d`](https://github.com/ugns/rss2socials/commit/92b867dadabc27cc8e5694f20076164dae7e5779))

- Update changelog to correct insertion marker ([#9](https://github.com/ugns/rss2socials/pull/9),
  [`92b867d`](https://github.com/ugns/rss2socials/commit/92b867dadabc27cc8e5694f20076164dae7e5779))

- Update post function to return a boolean indicating success
  ([#9](https://github.com/ugns/rss2socials/pull/9),
  [`92b867d`](https://github.com/ugns/rss2socials/commit/92b867dadabc27cc8e5694f20076164dae7e5779))

- Update post instructions template for clarity and tone consistency
  ([#9](https://github.com/ugns/rss2socials/pull/9),
  [`92b867d`](https://github.com/ugns/rss2socials/commit/92b867dadabc27cc8e5694f20076164dae7e5779))

### Features

- Add logging for loading and saving seen links with error handling
  ([#9](https://github.com/ugns/rss2socials/pull/9),
  [`92b867d`](https://github.com/ugns/rss2socials/commit/92b867dadabc27cc8e5694f20076164dae7e5779))


## v0.1.0 (2025-06-28)

### Bug Fixes

- **deps**: Update dependency openai to v1.92.2
  ([`4578962`](https://github.com/ugns/rss2socials/commit/4578962db060eb7e9b5343fb06efbd7fbe02cf35))

- **mergify**: Match all test matrix jobs for check-success
  ([`204f8d3`](https://github.com/ugns/rss2socials/commit/204f8d34d5b1cbe27ee63833f91f26e2a06b1e80))

- Update .mergify.yml to use check-success~=^test so Mergify recognizes all test matrix jobs (e.g.,
  test (3.9), test (3.10), etc.) as passing before queuing or merging PRs. - Ensures PRs are handled
  as expected when all test and

- **package**: Update dependency openai to v1.93.0
  ([#6](https://github.com/ugns/rss2socials/pull/6),
  [`9a55807`](https://github.com/ugns/rss2socials/commit/9a55807dfa0944399f1101d026cecc05faa037e3))

Co-authored-by: renovate[bot] <29139614+renovate[bot]@users.noreply.github.com>

Co-authored-by: mergify[bot] <37929162+mergify[bot]@users.noreply.github.com>

- **renovate**: Remove autodiscover and update commitMessage for compatibility
  ([`b9a4443`](https://github.com/ugns/rss2socials/commit/b9a44431cc2e89da110fc4c9d9ff5a79d16949cf))

- Remove 'autodiscover' option (not allowed in repo config). - Replace deprecated 'prTitle' with
  'commitMessage' string for PR title customization. - Ensure Renovate config is valid and

- **renovate**: Remove matchUpdateTypes from python dependencies rule
  ([`f53bba2`](https://github.com/ugns/rss2socials/commit/f53bba2668134244287404cba3a373b34ee57d7c))

- Resolve Renovate error by not combining matchUpdateTypes and allowedVersions in the same
  packageRule. - Python dependencies are now automerged and version-restricted to >=3.9 as intended.

### Features

- **core**: Initial codebase with modular structure, CLI, and Bluesky connector
  ([`44113ae`](https://github.com/ugns/rss2socials/commit/44113ae330691916dd9257e3a05398f435df1684))

- Add modular project structure under src/rss2socials/ - Implement CLI with dynamic connector
  discovery and extensible argument handling - Add common utilities for metadata, OpenAI, and RSS
  parsing - Add Bluesky connector with robust error handling and environment validation

- **mergify**: Enable batch merging of up to 5 PRs in merge queue
  ([`63fce2d`](https://github.com/ugns/rss2socials/commit/63fce2db73fcc28ede15557010812dcb866f58ff))

- Set batch_size: 5 in queue_rules to allow up to 5 PRs to be tested and merged together as a batch.
  - Improves throughput and efficiency for dependency and code updates. - Keeps all other queue and
  PR rules unchanged.

- **release**: Initial PyPI release
  ([`ec524a7`](https://github.com/ugns/rss2socials/commit/ec524a78310a048b06e13af24607220cd5b8570d))
