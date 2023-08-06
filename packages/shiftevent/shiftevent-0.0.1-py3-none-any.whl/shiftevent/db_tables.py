import sqlalchemy as sa


def define_tables(meta):
    """
    Creates table definitions and adds them to schema catalogue.
    Use your application schema when integrating into your app for migrations
    support and other good things.

    :param meta: metadata catalogue to add to
    :return: dict
    """
    tables = dict()

    # events
    tables['events'] = sa.Table('event_store', meta,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('created', sa.DateTime, nullable=False, index=True),
        sa.Column('type', sa.String(256), nullable=False, index=True),
        sa.Column('author', sa.String(256), nullable=False, index=True),
        sa.Column('object_id', sa.String(256), nullable=False, index=True),
        sa.Column('payload', sa.Text, nullable=True),
        sa.Column('payload_rollback', sa.Text, nullable=True),
    )

    return tables

