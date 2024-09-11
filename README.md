# 📋Simple Note
Simple Note(codename) is a table-based note-taking app that is based on Postgresql. You can easily create and use a table and foreign tables.

## Requirements
A database of Postgres.
Tables must have a primary key with a bigint type.

## Environment Variabl
- DatabaseURL
    - Database url for access.
        - See https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine

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
- Convert column types
- Expanding an array of self-referencing a column.

## Done
- Appending a foreign column
- Connecting between tables by foreign column.
- Expanding a Self-referencing column. 
- Tag filter 
- Using for any database of Postgresql. 
