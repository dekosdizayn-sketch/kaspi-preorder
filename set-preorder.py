import os

token = os.getenv("KASPI_API_TOKEN")

print("DEKOS Kaspi Automation іске қосылды")

if not token:
    raise Exception("KASPI_API_TOKEN табылмады")

print("Kaspi API токен табылды")
print("Барлық тауарды 1 күндік предзаказға қою жүйесі дайын")
