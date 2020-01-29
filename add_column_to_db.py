import sqlite3

dbCon = sqlite3.connect("/Users/dankufra/Downloads/Yassour_Orders_Budgets_DB.sqlite3")

cur = dbCon.cursor()

addColumn = "ALTER TABLE orders ADD COLUMN amount real DEFAULT 1"

cur.execute(addColumn)

change_around_order = ""
dbCon.close()

