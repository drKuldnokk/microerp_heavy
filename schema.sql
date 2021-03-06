BEGIN;
--
-- Create model Product
--
CREATE TABLE "sales_product" ("id" varchar(20) NOT NULL PRIMARY KEY, "name" varchar(500) NOT NULL);
--
-- Create model SalesLine
--
CREATE TABLE "sales_salesline" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "quantity" integer NOT NULL);
--
-- Create model SalesOrder
--
CREATE TABLE "sales_salesorder" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT);
--
-- Add field order_id to salesline
--
ALTER TABLE "sales_salesline" RENAME TO "sales_salesline__old";
CREATE TABLE "sales_salesline" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "quantity" integer NOT NULL, "order_id_id" integer NOT NULL REFERENCES "sales_salesorder" ("id"));
INSERT INTO "sales_salesline" ("order_id_id", "id", "quantity") SELECT NULL, "id", "quantity" FROM "sales_salesline__old";
DROP TABLE "sales_salesline__old";
CREATE INDEX "sales_salesline_564fd3cf" ON "sales_salesline" ("order_id_id");
--
-- Add field product_id to salesline
--
ALTER TABLE "sales_salesline" RENAME TO "sales_salesline__old";
CREATE TABLE "sales_salesline" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "quantity" integer NOT NULL, "order_id_id" integer NOT NULL REFERENCES "sales_salesorder" ("id"), "product_id_id" varchar(20) NOT NULL REFERENCES "sales_product" ("id"));
INSERT INTO "sales_salesline" ("order_id_id", "product_id_id", "id", "quantity") SELECT "order_id_id", NULL, "id", "quantity" FROM "sales_salesline__old";
DROP TABLE "sales_salesline__old";
CREATE INDEX "sales_salesline_564fd3cf" ON "sales_salesline" ("order_id_id");
CREATE INDEX "sales_salesline_5fdb567d" ON "sales_salesline" ("product_id_id");
COMMIT;


CREATE TABLE sales_popularity (
    product_id varchar(20) NOT NULL PRIMARY KEY REFERENCES sales_product (id),
    popularity integer
);

CREATE TRIGGER salesline_aft_insert AFTER INSERT ON sales_salesline
BEGIN  
    INSERT OR REPLACE INTO sales_popularity (product_id, popularity)
        VALUES (
            NEW.product_id_id,
            (SELECT SUM(value) FROM (
                SELECT popularity AS value FROM sales_popularity WHERE product_id = NEW.product_id_id
                UNION ALL 
                SELECT NEW.quantity AS value
            ))
        );
END;

CREATE TRIGGER salesline_aft_update AFTER UPDATE ON sales_salesline
BEGIN  
    INSERT OR REPLACE INTO sales_popularity (product_id, popularity)
        VALUES (
            OLD.product_id_id,
            (SELECT SUM(value) FROM (
                SELECT popularity AS value FROM sales_popularity WHERE product_id = OLD.product_id_id
                UNION ALL 
                SELECT -OLD.quantity AS value
            ))
        );
    INSERT OR REPLACE INTO sales_popularity (product_id, popularity)
        VALUES (
            NEW.product_id_id,
            (SELECT SUM(value) FROM (
                SELECT popularity AS value FROM sales_popularity WHERE product_id = NEW.product_id_id
                UNION ALL 
                SELECT NEW.quantity AS value
            ))
        );
END;

CREATE TRIGGER salesline_aft_delete AFTER DELETE ON sales_salesline
BEGIN  
    INSERT OR REPLACE INTO sales_popularity (product_id, popularity)
        VALUES (
            OLD.product_id_id,
            (SELECT SUM(value) FROM (
                SELECT popularity AS value FROM sales_popularity WHERE product_id = OLD.product_id_id
                UNION ALL 
                SELECT -OLD.quantity AS value
            ))
        );
END;