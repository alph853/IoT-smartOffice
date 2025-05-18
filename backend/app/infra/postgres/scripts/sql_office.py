GET_OFFICE_BY_ID = """
    SELECT * FROM offices WHERE id = $1;
"""

CREATE_OFFICE = """
    INSERT INTO offices (name, room, building, description) VALUES ($1, $2, $3, $4) RETURNING *;
"""

