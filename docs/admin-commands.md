# Admin Commands

These are owner/admin maintenance commands from `AdministrationCog` in `extensions/administration.py`.

## Access

- All commands in this page require the caller ID to be in `adminIds`.
- If a non-admin runs one, the bot now responds with a permission error.

## Command Reference

- `sync`
  - Syncs application commands to Discord.
  - Usage: `t.sync`

- `feedback <content>`
  - Stores internal feedback text.
  - Usage: `t.feedback <text>`

- `blockFeedback <user>`
  - Blocks a user from feedback features.
  - Usage: `t.blockFeedback @user`

- `unblockFeedback <user>`
  - Unblocks a user from feedback features.
  - Usage: `t.unblockFeedback @user`

- `test_bot`
  - Runs diagnostics suite.
  - Usage: `t.test_bot`

- `benchmark_bot`
  - Runs benchmark suite.
  - Usage: `t.benchmark_bot`

- `test_translation`
  - Sends a translation test output.
  - Usage: `t.test_translation`

- `update`
  - Runs maintenance steps and triggers restart endpoint.
  - Usage: `t.update`

- `welcome [user]`
  - Triggers welcome flow for a user (defaults to caller).
  - Usage: `t.welcome` or `t.welcome @user`

- `farewell [user]`
  - Triggers farewell flow for a user (defaults to caller).
  - Usage: `t.farewell` or `t.farewell @user`

- `onethingaboutmeichfahrautoseitvierjahreneinestageswolltichindenclubfahnichstandaneinerrotenampelundichwarganzalleinhintermirwareinbusunderfihrmirreinerhuptemichanhuphupichschaumiranwaspassiertistunderkommtraus`
  - Sends the hardcoded meme text.
  - Usage: `t.onethingaboutmeichfahrautoseitvierjahreneinestageswolltichindenclubfahnichstandaneinerrotenampelundichwarganzalleinhintermirwareinbusunderfihrmirreinerhuptemichanhuphupichschaumiranwaspassiertistunderkommtraus`

- `bsstarpoweremojis [start]`
  - Imports Brawl Stars star power emojis.
  - Usage: `t.bsstarpoweremojis` or `t.bsstarpoweremojis 10`

- `bsgadgetsemojis [start]`
  - Imports Brawl Stars gadget emojis.
  - Usage: `t.bsgadgetsemojis` or `t.bsgadgetsemojis 10`

- `bsaccdata <id>`
  - Fetches and prints Brawl Stars account data.
  - Usage: `t.bsaccdata <playerTagWithoutHash>`

- `editembedmessage`
  - Sends and edits a test embed message.
  - Usage: `t.editembedmessage`

- `setguildlocale <locale>`
  - Sets guild preferred locale.
  - Usage: `t.setguildlocale de`

- `testgithubauthtoken`
  - Runs a GitHub auth token localization path test.
  - Usage: `t.testgithubauthtoken`

- `testupdateuserroles`
  - Runs role update logic test.
  - Usage: `t.testupdateuserroles`

- `testgetcorrectnextnumber <mode> <numbers>`
  - Prints generated sequence for counting mode logic.
  - Usage: `t.testgetcorrectnextnumber 1 25`

- `sendUpdateTextToAllAdmins`
  - Sends update broadcast DM flow after multi-step confirmation.
  - Usage: `t.sendUpdateTextToAllAdmins`

- `sendDemoIsNoMoreToAllAdmins`
  - Sends demo-bot deprecation broadcast DM flow after confirmation.
  - Usage: `t.sendDemoIsNoMoreToAllAdmins`

- `me`
  - Shows bot identity in current guild.
  - Usage: `t.me`

- `permissionTest`
  - Prints composite permission test result for current channel.
  - Usage: `t.permissionTest`

- `permissionTest2`
  - Prints manage_messages permission test result for current channel.
  - Usage: `t.permissionTest2`

- `listPermissions [channel]`
  - Lists bot permissions for a channel (defaults to current).
  - Usage: `t.listPermissions` or `t.listPermissions #channel`

- `database_sync [url]`
  - Downloads/imports SQL dump (from attachment or URL), asks for schema selection, backs up current DB, recreates target schema, imports filtered SQL.
  - Usage:
    - `t.database_sync` with SQL file attached
    - `t.database_sync https://example.com/backup.sql`

## Error Responses

- Non-admin usage now returns an explicit permission error.
- Missing required arguments now return a specific missing-argument error.
- Invalid argument parsing now returns a command-usage error.
