# 📋Simple Note
Simple Note(codename) is a table-based note-taking app that is based on Postgresql. You can easily create and use a table and foreign tables.

## Requirements
A database of Postgres.
Tables must have a primary key with a bigint type.

## Environment Variabl
- SN_ADDRESS
    - An address of database.
- SN_DEFAULT_TIMEZONE
    - A default timezone of this app.

## Custom Database Types
- url
    - A column that includes url.
    - e.g. A site's row
- image_url
    - An image as url.
- text_with_tag
    - A text with tags.


## Roadmap
- Column type of Interval support (e.g. duration)
- Multiple timers and stopwatches
- Customization of the clock such as hours from wake up.
- Customization of the dashboard.

## Done
- Appending a foreign column
- Expanding an array of self-referencing a column.
- Convert column types.
- Connecting between tables by foreign column.
- Expanding a Self-referencing column. 
- Tag filter 
- Using for any database of Postgresql. 
