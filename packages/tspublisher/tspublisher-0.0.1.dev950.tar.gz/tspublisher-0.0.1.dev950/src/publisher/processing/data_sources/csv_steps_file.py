from __future__ import absolute_import, division, print_function, unicode_literals

import sqlite3

from publisher import settings


def get_csv_steps_file(phase_code):
    c = sqlite3.connect(settings.CONTENT_DB_DIR)
    cursor = c.execute("""
        SELECT f.file_path FROM assetdb_asset a
        INNER JOIN assetdb_assetversion v ON a.id = v.asset_id
        INNER JOIN assetdb_assetfile f ON v.id = f.asset_version_id
        WHERE
            a.category = 'Admin' AND
            a."name" = 'Main' AND
            a."level_of_detail" = 'default' AND
            a."variant" = 'default' AND
            a."module" = ? AND
            a."asset_type" = 'csvSteps' AND
            a."department" = 'default' AND
            a."operation" IS NULL AND
            a."institution" = 'TouchSurgeryContent' AND
            a."stage" = 'default' AND
            NOT a.deprecated AND
            NOT v."pending" AND
            NOT v."deprecated" AND
            NOT f."pending" AND
            NOT f."deprecated" AND
            f."name" = 'default'
        ORDER BY v."version" DESC LIMIT 1;""", (phase_code,))

    row = cursor.fetchone()
    c.close()

    return _get_platform_specific_path(row[0].strip()) if row else None


def _get_platform_specific_path(file_path):
    if settings.ORIGINAL_CONTENT_ROOT in file_path:
        file_path = file_path.replace(settings.ORIGINAL_CONTENT_ROOT, settings.REPLACEMENT_CONTENT_ROOT, 1)
    else:
        file_path = file_path.replace(settings.ORIGINAL_CONTENT_ROOT_OLD, settings.REPLACEMENT_CONTENT_ROOT_OLD, 1)

    return file_path.replace("\\", "/")
