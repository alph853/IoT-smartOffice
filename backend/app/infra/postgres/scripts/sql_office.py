
GET_ALL_OFFICES = """
    SELECT * FROM office;
"""

GET_OFFICE_BY_ID = """
    SELECT * FROM office WHERE id = $1;
"""

CREATE_OFFICE = """
    INSERT INTO office (name, room, building, description) VALUES ($1, $2, $3, $4) RETURNING *;
"""

UPDATE_OFFICE = """
    UPDATE office SET name = $2, room = $3, building = $4, description = $5 WHERE id = $1 RETURNING *;
"""

DELETE_OFFICE = """
    DELETE FROM office WHERE id = $1;
"""

