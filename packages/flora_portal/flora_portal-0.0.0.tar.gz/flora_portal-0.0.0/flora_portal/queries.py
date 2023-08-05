BROWSE = """
SELECT
  taxa.id,
  taxa.name_simple
FROM taxa
INNER JOIN floras
  ON taxa.flora_id = floras.id
WHERE floras.id = %s
ORDER BY name_simple
"""

SELECT_TREATMENT = """
SELECT
  floras.flora,
  taxa.name_simple,
  taxa.name_html,
  taxa.parent_id,
  parents.name_simple,
  treatments.description, treatments.phenology,
  treatments.habitat, treatments.distribution,
  treatments.notes,
  GROUP_CONCAT(common_names.common_name SEPARATOR ', ')
FROM taxa
INNER JOIN floras
  ON taxa.flora_id = floras.id
LEFT JOIN common_names
  ON taxa.id = common_names.taxon_id
LEFT JOIN treatments
  ON taxa.id = treatments.taxon_id
LEFT JOIN taxa AS parents
  ON taxa.parent_id = parents.id
WHERE taxa.id = %s
GROUP BY taxa.id
"""

UPDATE_TREATMENT = """
UPDATE treatments
INNER JOIN taxa
  ON taxa.id = treatments.taxon_id
SET
  treatments.description = %s,
  treatments.phenology = %s,
  treatments.habitat = %s,
  treatments.distribution = %s,
  treatments.notes = %s
WHERE taxa.id = %s
"""

SELECT_IMAGES = """
SELECT CONCAT(CAST(id AS CHAR(10)), ".", file_extension)
FROM images
WHERE taxon_id = %s
"""

SELECT_OCCURRENCES = """
SELECT
  latitude,
  longitude
FROM occurrences
WHERE taxon_id = %s
"""

SELECT_USER = """
SELECT
  id,
  is_admin,
  password_hash
FROM users
WHERE username = %s
"""

CHECK_USER_ACCESS = """
SELECT 1
FROM user_access
INNER JOIN floras
  ON user_access.flora_id = floras.id
WHERE user_access.user_id = %s
  AND floras.id = %s
LIMIT 1
"""

INSERT_TAXON = """
INSERT INTO taxa (
  flora_id,
  parent_id,
  name_simple,
  name_html,
  name_markup,
  taxon_rank)
VALUES (%s, %s, %s, %s, %s, %s)
"""

INSERT_TREATMENT = """
INSERT INTO treatments (
  taxon_id,
  description,
  phenology,
  habitat,
  distribution,
  notes)
VALUES (%s, %s, %s, %s, %s, %s)
"""

INSERT_OCCURRENCE = """
INSERT INTO occurrences (
  taxon_id,
  latitude,
  longitude)
VALUES (%s, %s, %s)
"""

CHECK_USER_ACCESS_BY_TAXON = """
SELECT 1 FROM user_access
INNER JOIN floras
  ON user_access.flora_id = floras.id
WHERE user_access.user_id = %s
  AND floras.id = (SELECT flora_id FROM taxa
                   WHERE id = %s)
LIMIT 1
"""

INSERT_IMAGE = """
INSERT INTO images (
  taxon_id,
  file_extension)
VALUES (%s, %s)
"""

SELECT_USER_ACCESS = """
SELECT floras.flora
FROM floras
INNER JOIN user_access
  ON user_access.flora_id = floras.id
WHERE user_access.user_id = %s
"""

