## [1.5.4] - 2018-06-19
### Added
- Added methods for getting event counts from accounts and subjects (modules, gateways)

## [1.5.4b2] - 2018-06-11
### Fixed
- Fixed paging for retrieving larger volumes of messages

## [1.5.4b1] - 2018-05-07
### Added
- Support for additional node types
- Unpacking LTE-M specific module packet signal data
- Added method to get a subject's last seen time.
- Added method to get all nodes associated with an application token.
- Added support for Asset Groups (Create Groups, Delete Groups, Get Groups,
  Add Modules, Remove Modules, Get Modules, and Rename Groups)
### Fixed
- Remove dependence on sometime non-present fields in API uplink events
- Fixed HTTP calls in retrieving status messages

## [1.5.2] - 2017-2-1
### Fixed
- Set gateway's network token to None instead of throwing `KeyError` when
gateway has not been registered.

## [1.5.1] - 2017-1-4
### Added
- Added user-settable "on_close" callback for subscriptions.

### Changed
- Default UplinkMessage.network_token to None if it's not set in Conductor.

## [1.5.0] - 2016-10-28
### Changed
- Implement __eq__ and others for classes.
- Use Conductor's "next page" concept to split large queries into multiple
requests.

### Deprecated
- Deprecate get_messages_time_range_chunked, as chunking large queries
is now handled automatically.

## [1.4.0] - 2016-9-19
### Added
- Initial release. Includes functionality for querying data and metadata
for uplink messages from app tokens, network tokens, gateways, modules,
and accounts.
- Can send downlink messages to modules (unicast) and app tokens (multicast).
- Can query for status of downlink messages and cancel downlink messages.
- Can get data about subjects through the common _data attribute.
