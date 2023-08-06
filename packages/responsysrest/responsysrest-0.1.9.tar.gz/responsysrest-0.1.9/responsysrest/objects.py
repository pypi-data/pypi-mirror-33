class table:
    """
    A table as it relates to an object that will be in Responsys.

    There are three basic types: Profile List, Profile Extension Table,
    and Supplemental Table. Tables are in Responsys in a specified folder.
    """

    def __init__(self, name, folder, ri_type, fields, records):
        """A table exist with these properties."""
        # The name of the table
        self.name = name
        # The name of the folder it resides in
        self.folder = folder
        # The Responsys Interact type of table
        # One of: Profile, Profile Extension, or Supplemental
        self.ri_type = ri_type
        self.fields = fields
        self.records = records

    def create(name, folder, ri_type, records):
        """Create a table."""
        return

    def merge(name, ri_type, fields, records):
        """Merge records into a table."""
        return

    def delete(name):
        """Delete a table."""
        return


class member:
    """A member of your Responsys Interact or local application."""

    def __init__(self, record_ids, tables):
        """A member is just the records and tables associated."""
        self.record_ids = record_ids
        self.tables = tables


class member_of_table:
    """A member of a table."""

    def __init__(self, record_id, table, data):
        """
        Responsys has different access methods for records per id type.

        One of RIID, email address, customer id, or mobile number.
        """
        self.record_id = record_id
        self.table = table
        self.data = data

    def create(record_id, table, data=None):
        """Create a member in a table with data."""
        return

    def retrieve(record_id, table):
        """Retrieve the record data for a member of a table in Interact."""
        return

    def delete(record_id, table):
        """Delete the record and data of a member in a specific table."""
        return
