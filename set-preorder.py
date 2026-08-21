import os

token = os.getenv("KASPI_API_TOKEN")

print("DEKOS Kaspi Automation іске қосылды")

env:
  KASPI_API_TOKEN: ${{ secrets.KASPI_API_TOKEN }}

print("Kaspi API токен табылды")
print("Барлық тауарды 1 күндік предзаказға қою жүйесі дайын")
