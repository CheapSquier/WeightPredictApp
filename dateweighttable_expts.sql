SELECT * FROM date_weight_pairs.dateweighttable;

SHOW FULL TABLES FROM `date_weight_pairs`;dateweighttabledateweighttable
SHOW CREATE TABLE `dateweighttable`;
DROP TABLE dateweighttable;
SELECT @@global.read_only;
SET GLOBAL read_only = OFF;

BEGIN;
INSERT INTO dateweighttable (date, weight) VALUES (date, weight);
('2020-07-30', 50)
END;

BEGIN;
INSERT INTO dateweighttable (date, weight) VALUES (%(date)s, %(weight)s)
({'date': '2020-7-17', 'weight': 170.8}, 
 {'date': '2020-7-18', 'weight': 170.4}, 
 {'date': '2020-7-19', 'weight': 170.8}, 
 {'date': '2020-7-20', 'weight': 170.6}, 
 {'date': '2020-7-21', 'weight': 170.6}, 
 {'date': '2020-7-22', 'weight': 745.0})
END;

INSERT INTO dateweighttable (date, weight) 
	VALUES
		('2020-7-18', 170.4), 
		('2020-7-19', 170.8), 
		('2020-7-20', 170.6), 
		('2020-7-21', 170.6), 
		('2020-7-22', 170.6),
		('2020-7-23', 170.0), 
		('2020-7-24', 170.4), 
		('2020-7-25', 170.4), 
		('2020-7-26', 170.6), 
		('2020-7-27', 170.8),
		('2020-7-28', 170.4), 
		('2020-7-29', 168.6), 
		('2020-7-30', 169.6), 
		('2020-7-31', 170.4), 
		('2020-8-01', 170.2),
		('2020-8-02', 170.2);
COMMIT;

DELETE FROM dateweighttable  
	WHERE date IN
		('2020-7-17', '2020-7-18', '2020-7-19', '2020-7-20', '2020-7-21',
        '2020-7-22', '2020-7-30', '2020-7-31');
COMMIT;

-- This won't work since we have safe update mode enabled
DELETE FROM dateweighttable;
COMMIT;

INSERT INTO dateweighttable (date, weight) VALUES ('2020-07-31', 50);

INSERT INTO dateweighttable VALUES('2020-07-30', 50);

DELETE FROM dateweighttable WHERE date='2020-08-04';

INSERT INTO users (`index`, name, color) VALUES (%(index)s, %(name)s, %(color)s)
({'index': 0, 'name': 'User 1', 'color': 'purple'}, 
 {'index': 1, 'name': 'User 2', 'color': 'rose'}, 
 {'index': 2, 'name': 'User 3', 'color': 'yellow'});
COMMIT;

SELECT date FROM date_weight_pairs.dateweighttable
WHERE EXISTS (SELECT date FROM date_weight_pairs.dateweighttable WHERE date='2020-07-19');

SELECT date FROM date_weight_pairs.dateweighttable WHERE date='2020-7-19';