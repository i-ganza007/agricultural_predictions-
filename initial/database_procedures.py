from sqlalchemy import text
from db_schema_file import engine
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_stored_procedures_and_triggers():
    with engine.begin() as conn:  # Use begin() for transaction management

        # Drop and create CalculateItemYieldAverage procedure
        logger.info("Creating CalculateItemYieldAverage procedure...")
        conn.execute(text("""
        DROP PROCEDURE IF EXISTS CalculateItemYieldAverage;
        """))
        conn.execute(text("""
        CREATE PROCEDURE CalculateItemYieldAverage(IN item_id_param INT)
        BEGIN
            SELECT 
                i.item_name,
                AVG(y.hg_per_ha_yield) as average_yield,
                MIN(y.hg_per_ha_yield) as min_yield,
                MAX(y.hg_per_ha_yield) as max_yield
            FROM yield y
            JOIN items i ON y.item_id = i.item_id
            WHERE y.item_id = item_id_param
            GROUP BY i.item_name;
        END;
        """))

        # Drop and create GetAreaEnvironmentStats procedure
        logger.info("Creating GetAreaEnvironmentStats procedure...")
        conn.execute(text("""
        DROP PROCEDURE IF EXISTS GetAreaEnvironmentStats;
        """))
        conn.execute(text("""
        CREATE PROCEDURE GetAreaEnvironmentStats(IN area_id_param INT)
        BEGIN
            SELECT 
                a.area_name,
                e.year,
                AVG(e.temp) as avg_temperature,
                AVG(e.average_rai) as avg_rainfall,
                AVG(e.pesticides_tavg) as avg_pesticides
            FROM environment e
            JOIN areas a ON e.area_id = a.area_id
            WHERE e.area_id = area_id_param
            GROUP BY a.area_name, e.year
            ORDER BY e.year DESC;
        END;
        """))

        # Drop and create PredictYield procedure
        logger.info("Creating PredictYield procedure...")
        conn.execute(text("""
        DROP PROCEDURE IF EXISTS PredictYield;
        """))
        conn.execute(text("""
        CREATE PROCEDURE PredictYield(
            IN area_id_param INT,
            IN item_id_param INT,
            IN temp_param FLOAT,
            IN rain_param FLOAT,
            IN pesticides_param FLOAT
        )
        BEGIN
            DECLARE avg_yield FLOAT;
            DECLARE temp_coef FLOAT DEFAULT 0.5;
            DECLARE rain_coef FLOAT DEFAULT 0.3;
            DECLARE pest_coef FLOAT DEFAULT -0.2;

            SELECT AVG(hg_per_ha_yield) INTO avg_yield
            FROM yield
            WHERE area_id = area_id_param AND item_id = item_id_param;

            SELECT 
                avg_yield + 
                (temp_param * temp_coef) + 
                (rain_param * rain_coef) + 
                (pesticides_param * pest_coef) 
            AS predicted_yield;
        END;
        """))

        # Drop and create FindTopProducingAreas procedure
        logger.info("Creating FindTopProducingAreas procedure...")
        conn.execute(text("""
        DROP PROCEDURE IF EXISTS FindTopProducingAreas;
        """))
        conn.execute(text("""
        CREATE PROCEDURE FindTopProducingAreas(
            IN item_id_param INT, 
            IN year_param INT, 
            IN limit_param INT
        )
        BEGIN
            SELECT 
                a.area_name,
                y.hg_per_ha_yield,
                y.year,
                RANK() OVER (ORDER BY y.hg_per_ha_yield DESC) AS yield_rank
            FROM yield y
            JOIN areas a ON y.area_id = a.area_id
            WHERE y.item_id = item_id_param AND y.year = year_param
            ORDER BY y.hg_per_ha_yield DESC
            LIMIT limit_param;
        END;
        """))

        # Create yield_logs table if it doesn't exist
        logger.info("Creating yield_logs table if not exists...")
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS yield_logs (
            log_id INT AUTO_INCREMENT PRIMARY KEY,
            area_id INT,
            item_id INT,
            year INT,
            action VARCHAR(10),
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """))

        # Drop and create after_yield_insert trigger
        logger.info("Creating after_yield_insert trigger...")
        conn.execute(text("""
        DROP TRIGGER IF EXISTS after_yield_insert;
        """))
        conn.execute(text("""
        CREATE TRIGGER after_yield_insert
        AFTER INSERT ON yield
        FOR EACH ROW
        BEGIN
            INSERT INTO yield_logs (area_id, item_id, year, action)
            VALUES (NEW.area_id, NEW.item_id, NEW.year, 'INSERT');
        END;
        """))

        logger.info("All procedures and trigger created successfully.")


# Optional: A helper function to insert sample yield data to test the trigger
def insert_sample_yield(area_id, item_id, year, hg_per_ha_yield):
    with engine.begin() as conn:
        conn.execute(
            text("""
            INSERT INTO yield (area_id, item_id, year, hg_per_ha_yield)
            VALUES (:area_id, :item_id, :year, :yield)
            """),
            {"area_id": area_id, "item_id": item_id, "year": year, "yield": hg_per_ha_yield}
        )
        logger.info(f"Inserted sample yield data: area_id={area_id}, item_id={item_id}, year={year}, yield={hg_per_ha_yield}")

