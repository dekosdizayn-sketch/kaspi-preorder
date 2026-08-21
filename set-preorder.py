import os

token = os.getenv("KASPI_TOKEN")

print("DEKOS Kaspi Automation іске қосылды")

if not token:
    raise Exception("KASPI_TOKEN табылмады")

print("Kaspi API токен табылды")
print("Барлық тауарды 1 күндік предзаказға қою жүйесі дайын")
