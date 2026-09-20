import csv
from pathlib import Path
from app.database.db import connect
async def export_table(table,path):
 allowed={'users','products','categories','orders','services','wallet_transactions','withdrawals','audit_logs','discount_codes','tutorials'}
 if table not in allowed: raise ValueError('table not allowed')
 db=await connect(); cur=await db.execute(f'SELECT * FROM {table}'); rows=await cur.fetchall(); headers=[x[0] for x in cur.description]; Path(path).parent.mkdir(parents=True,exist_ok=True)
 with open(path,'w',encoding='utf-8-sig',newline='') as f:
  w=csv.writer(f); w.writerow(headers); w.writerows([tuple(r) for r in rows])
 await db.close()
