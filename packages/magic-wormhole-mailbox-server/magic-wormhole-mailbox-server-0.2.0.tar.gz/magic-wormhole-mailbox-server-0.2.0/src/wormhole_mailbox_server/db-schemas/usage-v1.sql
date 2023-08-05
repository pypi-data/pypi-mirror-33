CREATE TABLE `version`
(
 `version` INTEGER -- contains one row, set to 1
);

CREATE TABLE `current`
(
 `rebooted` INTEGER, -- seconds since epoch of most recent reboot
 `updated` INTEGER, -- when `current` was last updated
 `blur_time` INTEGER, -- `started` is rounded to this, or None
 `connections_websocket` INTEGER -- number of live clients via websocket
);

-- one row is created each time a nameplate is retired
CREATE TABLE `nameplates`
(
 `app_id` VARCHAR,
 `started` INTEGER, -- seconds since epoch, rounded to "blur time"
 `waiting_time` INTEGER, -- seconds from start to 2nd side appearing, or None
 `total_time` INTEGER, -- seconds from open to last close/prune
 `result` VARCHAR -- happy, lonely, pruney, crowded
 -- nameplate moods:
 --  "happy": two sides open and close
 --  "lonely": one side opens and closes (no response from 2nd side)
 --  "pruney": channels which get pruned for inactivity
 --  "crowded": three or more sides were involved
);
CREATE INDEX `nameplates_idx` ON `nameplates` (`app_id`, `started`);

-- one row is created each time a mailbox is retired
CREATE TABLE `mailboxes`
(
 `app_id` VARCHAR,
 `for_nameplate` BOOLEAN, -- allocated for a nameplate, not standalone
 `started` INTEGER, -- seconds since epoch, rounded to "blur time"
 `total_time` INTEGER, -- seconds from open to last close
 `waiting_time` INTEGER, -- seconds from start to 2nd side appearing, or None
 `result` VARCHAR -- happy, scary, lonely, errory, pruney
 -- rendezvous moods:
 --  "happy": both sides close with mood=happy
 --  "scary": any side closes with mood=scary (bad MAC, probably wrong pw)
 --  "lonely": any side closes with mood=lonely (no response from 2nd side)
 --  "errory": any side closes with mood=errory (other errors)
 --  "pruney": channels which get pruned for inactivity
 --  "crowded": three or more sides were involved
);
CREATE INDEX `mailboxes_idx` ON `mailboxes` (`app_id`, `started`);
CREATE INDEX `mailboxes_result_idx` ON `mailboxes` (`result`);
